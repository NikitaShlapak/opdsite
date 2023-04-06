import logging


import vk_api
from django.core.management import BaseCommand
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from ...models import *
from ....SNO.env import VK_TOKEN


logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")





class Command(BaseCommand):
    help = 'BOT'
    application_mode = False
    def handle(self, *args, **options):
        def sender(text='Info-Test', **kwargs):
            logging.debug(f"Send message: {text=} to {kwargs}")
            return vk.messages.send(**kwargs, message=text, random_id=0)

        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        logging.info("Bot initialized")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                msg = event.text
                self.id = event.user_id
                logging.debug(f"Received message: {msg=} from {self.id=}")

                if msg == 'список событий':
                    events = Event.objects.all()
                    data =  f'Найдено событий: {len(events)}\nСписок событий:\n'+'\n'.join([str(ev) for ev in events])


                    print(msg, events)
                    sender(user_id=self.id, text=data)
                elif msg == 'подать заявку':
                    events = Event.objects.all()
                    data = 'Список событий:\n' + '\n'.join([str(ev) for ev in events])

                    keyboard = VkKeyboard(one_time=True)
                    for ev in events:
                        keyboard.add_button(ev.title)

                    sender(user_id=self.id, text=f'{data}\n\nВыберите интересующее вас событие',
                           keyboard=keyboard.get_keyboard())
                elif msg == 'Подтвердить заявку':
                    self.application_mode = False
                    try:
                        #app = Application.objects.create(user_id=self.id,event=events[0])
                        self.app.save()
                    except:
                        text = "Ваша заявка не принята"
                    else:
                        text = "Ваша заявка принята"
                    sender(user_id=self.id, text=text)
                elif msg == 'Отозвать заявку':
                    self.application_mode = False
                else:
                    if self.application_mode:
                        self.app.data = msg
                        text = f"""Заявка на мероприятие
                        {self.app.event}
                        Данные о студенте:
                        {self.app.data}                        
                        """
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button("Подтвердить заявку")
                        keyboard.add_button("Отозвать заявку")

                        sender(user_id=self.id, text=text, keyboard=keyboard.get_keyboard())
                    else:
                        events = Event.objects.filter(title=msg)

                        if len(events)>1:
                            text = f'Найдено событий: {len(events)}\n'
                        elif len(events)<1:
                            text = 'Неизвестная команда'
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button("список событий")
                            keyboard.add_button("подать заявку")
                        else:
                            if Application.objects.filter(user_id=self.id, event=events[0]):
                                text = 'Вы уже подавали заявку на это мероприятие'
                            else:
                                self.application_mode = True
                                self.app = Application.objects.create(user_id=self.id, event=events[0])
                                text = "Укажите ваши данные: ФИО и группу"


                        kwargs = {'user_id' : self.id, 'text' : text}
                        if keyboard:
                            kwargs['keyboard']=keyboard
                        sender(**kwargs)
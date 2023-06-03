class WikiPlainHTMLTextTransformer:
    def fit(self, text:str):
        return self.fit_plain(text)
    def fit_plain(self, text:str):
        text = text.replace(self.u[0], '<u>').replace(self.u[1], '</u>').replace(self.i[0], '<i>').replace(self.i[1], '</i>').replace(self.b[0], '<b>').replace(self.b[1], '</b>').replace(self.hr, '<hr>')
        text = text.replace(self.olist[0], '<ol>').replace(self.olist[-1], '</ol>').replace(self.ulist[0], '<ul>').replace(self.ulist[-1], '</ul>')
        text = text.replace(self.olist[1], '<li>').replace(self.olist[2], '</li>').replace(self.ulist[1], '<li>').replace(self.ulist[2], '</li>')
        text = text.replace(self.table[0], '<table class="table table-primary table-bordered text-center align-middle">').replace(self.table[-1], '</table>')
        text = text.replace(self.table[1], '<tr>').replace(self.table[2], '<td>').replace(self.table[3], '</tr>').replace(self.table[4], '</td>')
        text_split = text.split('\r\n')
        new_text = ''
        for i in range(len(text_split)):
            line = text_split[i]
            print(f"1|{line}|")
            line = line.strip()
            if not len(line):
                line = '<br>'
            if line.startswith(self.h):
                if line.startswith(self.h * 2):
                    if line.startswith(self.h * 3):
                        line = f'<h6>{line[3:]}</h6>'
                    else:
                        line = f'<h5>{line[2:]}</h5>'
                else:
                    line = f'<h4>{line[1:]}</h4>'
            if not (line.endswith('<hr>') or line.endswith('<br>') or
                    line.endswith('<h4>') or line.endswith('</h4>') or
                    line.endswith('<h5>') or line.endswith('</h5>') or
                    line.endswith('<h6>') or line.endswith('</h6>') or
                    line.endswith('<tr>') or line.endswith('</tr>') or
                    line.endswith('<td>') or line.endswith('</td>') or
                    line.endswith('<li>') or line.endswith('</li>') or
                    line.endswith('<ol>') or line.endswith('</ol>') or
                    line.endswith('<ul>') or line.endswith('</ul>') or
                    line.endswith('<table class="table table-primary table-bordered text-center align-middle">') or line.endswith('</table>')
            ):
                line = line + '<br>'
            new_text = new_text + line
            print(f"2|{line}|")
        return new_text


    def __init__(self,
                     h = '#',
                     u = '{{ }}'.split(' '),
                     i = '(( ))'.split(' '),
                     b = '[[ ]]'.split(' '),
                     hr = '---',
                     olist = '<<olist>> <<newline>> <<endline>> <<endolist>>'.split(' '),
                     ulist = '<<ulist>> <<newline>> <<endline>> <<endulist>>'.split(' '),
                     table = '<<table>> <<newrow>> <<newcol>> <<endrow>> <<endcol>> <<endtable>>'.split(' ')
                 ):
        self.h = h
        self.u = u
        self.i = i
        self.b = b
        self.hr = hr
        self.olist = olist
        self.ulist = ulist
        self.table = table

def form_title(page='main'):
    title = 'Главная | Main'
    if page == 'opened':
        title = 'Открытые | Opened'
    if page =='closed':
        title = 'Закрытые | Closed'
    if page =='under_review' :
        title = 'На проверке | Under review'
    if page =='rejected':
        title = 'Отклонённые | Rejected'
    if page =='external':
        title = 'Внешние | External'
    if page =='service':
        title = 'Сервисные | Service'
    if page =='research':
        title = 'Исследовательские | Research'
    if page == 'register':
        title = 'Регистрация | Register'
    if page == 'login':
        title = 'Вход | Login'
    if page == 'profile':
        title = 'Личный кабинет | Profile'
    if page == 'marking':
        title = 'Оценка отчёта | Report marking'
    return title
from .main import Main

class CBtcmanager(Main):
    def __init__(self, link, posts, handbook):
        Main.__init__(self, link, posts, handbook)

        self.menu = [
            'Bitcoin', 'Blockchain News', 'Ethereum News',
            'Mining News', 'Finance News', 'Business News',
            'Technology', 'Commentary', 'Commentary',
            'Press Releases', 'Regulation News', 'Entertainment News',
            'Interviews News', 'News Digest', 'Altcoins News', 'ICO News'
        ]

        self.result = []

    def start(self):
        try:
            menu = self.get_menu('id', 'menu-topmenu')

            for page in menu:
                self.get_news(page['url'], page['title'])

            self.log.write("End: added {0} posts".format(len(self.result)))
        except RuntimeError as error:
            self.log.write("Error: {0}".format(error))

    def get_news(self, url, section):
        self.set_file(url)

        soup = self.soup()

        wrapper = soup.find('div', {'class': 'article_list'})

        try:
            blocks = wrapper.find_all('section', {'class': None})
        except AttributeError:
            raise RuntimeError("structure of the news list has changed")

        for block in blocks:
            url = self.check_url(block.find('a', {'class': 'readmore'}).get('href'))
            title = block.find('h2').text.strip()

            if title in self.posts:
                continue

            try:
                post = self.get_post(url)

                if self.check_date(post['date'], False, "%B %d, %Y %H:%M") is None:
                    break

                if post:
                    handbook = self.check_handbook_post(title, post['content'])

                    if handbook:
                        self.result.append({
                            'url': url,
                            'title': title,
                            'date': post['date'],
                            'section': section,
                            'text': post['content'],
                            'handbook': handbook
                        })

                        self.posts.append(title)

            except Warning as error:
                self.log.write("Error: {0}".format(error))

    def get_post(self, url):
        if url is None:
            return

        self.set_file(url)

        soup = self.soup()

        content = soup.find('div', {'itemprop': 'articleBody'})
        date = soup.find('time', {'pubdate': 'pubdate'})

        if content is None or date is None:
            raise Warning("structure of the news post has changed. Post link: {0}".format(url))

        text = []
        for div in content.find_all('div'):
            if not div is None:
                div.extract()

        for p in content.find_all('p'):
            script = p.script

            if not script is None:
                script.extract()

            text.append(self.clear(p.text))

        return {
            'content': '<br>'.join(text),
            'date': date.text.strip()
        }
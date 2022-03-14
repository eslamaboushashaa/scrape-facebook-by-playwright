from bs4.element import Tag
from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import base64
import plotly.graph_objects as go

class parse_facebook:

    def go_to_page(self, page_url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(page_url)
            except:
                print('Please, put right link')
            # this code make webdriver scroll down
            page.evaluate(
                '''
                var intervalID = setInterval(function () {
                var scrollingElement = (document.scrollingElement || document.body);
                scrollingElement.scrollTop = scrollingElement.scrollHeight;
                }, 200);
                ''')
            prev_height = None
            """ 
            sometime facebook show page to login 
            i make click to remove login page and continue scroll
            
            make the mouse scroll up to make program restart
            """
            try:
                item_close = page.locator("[aria-label=\"Close\"]").click()
                if item_close is not None:
                    item_close.click()
                    page.mouse.wheel(-1000, 0)
            except :
                pass
            while True:
                curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
                if not prev_height:
                    prev_height = curr_height
                    time.sleep(10)
                elif prev_height == curr_height:
                    page.evaluate('clearInterval(intervalID)')
                    break
                else:
                    prev_height = curr_height
                    time.sleep(10)
            selector = page.query_selector('div.rq0escxv.l9j0dhe7.du4w35lb')
        # I save html code in variable to parse it by beautifulSoup
            html = selector.inner_html()
            return html

    def extract_data(self, html):
        # i use lxml because it is very fast
        soup = BeautifulSoup(html, 'lxml')

        # facebook don't show number fo follwers
        #followers_element = soup.select_one('a.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.m9osqain.lrazzd5p:first-child')
        #if followers_element is not None:
        #    followers = followers_element.get_text()
        # make all variable in list to marge lists to create DataFrame
        all_date = []
        all_react = []
        list_no_com = []
        list_no_share = []
        posts  = soup.select('div.rq0escxv.l9j0dhe7.du4w35lb.hybvsw6c.io0zqebd.m5lcvass.fbipl8qg.nwvqtn77.k4urcfbm.ni8dbmo4.stjgntxs.sbcfpzgs')
        for post in posts:
            # extract date from each post
            date = post.select_one('span.tojvnm2t.a6sixzi8.abs2jz4q.a8s20v7p.t1p8iaqh.k5wvi7nf.q3lfd5jv.pk4s997a.bipmatt0.cebpdrjk.qowsmv63.owwhemhu.dp1hu0rb.dhp61c6y.iyyx5f41>a>span')
            if date is not None:
                l = date.get_text()
                all_date.append(l)
            # no of react in each post
            try:
                react = post.select_one('span.bzsjyuwj.ni8dbmo4.stjgntxs.ltmttdrg.gjzvkazv>span>span').get_text()
                all_react.append(react)
            except AttributeError:
                all_react.append('0')
            # no of comment in each post
            try:
                comment = post.select_one('div.gtad4xkn:nth-child(1)')
                comment_no = comment.select_one('span.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.b0tq1wua.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d9wwppkn.hrzyx87i.jq4qci2q.a3bd9o3v.b1v8xokw.m9osqain').get_text()
                list_no_com.append(comment_no)
            except AttributeError:
                list_no_com.append('0')
            # no of share in each post
            try:
                share = post.select_one('div.gtad4xkn:nth-child(2)')
                share_no = share.select_one('span.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.b0tq1wua.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d9wwppkn.hrzyx87i.jq4qci2q.a3bd9o3v.b1v8xokw.m9osqain').get_text()
                list_no_share.append(share_no)
            except AttributeError:
                list_no_share.append('0')

        #no_posts = len(posts)
        return all_date, all_react , list_no_com, list_no_share

    def clean_and_create_DF(self, all_date, all_react, list_no_comm, list_no_share):
        # remove the top 2 row in each list to make all list have same length
# facebook create dummy post so we should remove this dummy posts to create true dataframe
        # this line in button give us the bummy posts
        dummy_post = len(all_react) - len(all_date)
        # remove the dummy posts
        react = all_react[dummy_post:]
        no_comm = list_no_comm[dummy_post:]
        no_share = list_no_share[dummy_post:]

        data = {'Date': all_date,'React':react, 'Comment':no_comm, 'Share':no_share}
        df = pd.DataFrame(data = data)

        #clean data
# extract number from text in comments and share
        df['Comment']= df['Comment'].str.extract('(\d+)')
        df['Share']= df['Share'].str.extract('(\d+)')


        # convert date from object into time type

# convert reacts from object into int
        df['React']=pd.to_numeric(df['React'])
# convert comments type into int type
        df['Comment']=pd.to_numeric(df['Comment'])
# convert shares type into int type
        df['Share']=pd.to_numeric(df['Share'])
        return df
    def download_data_csv(self, object_to_download, download_filename, download_link_text):
        """
           Generates a link to download the given object_to_download.

           object_to_download (str, pd.DataFrame):  The object to be downloaded.
           download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
           download_link_text (str): Text to display for download link.

           Examples:
           download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
           download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

           """
        if isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

            # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

        return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

    def visualise_data(self, df):
        # this layout for all graphs
        layout_react = go.Layout(
            plot_bgcolor="#FFF",  # Sets background color to white
            xaxis=dict(
                title='Date',
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title='React',
                linecolor="#BCCCDC",  # Sets color of Y-axis line
                showgrid=False,  # Removes Y-axis grid lines
            )
        )
        layout_comment = go.Layout(
            plot_bgcolor="#FFF",  # Sets background color to white
            xaxis=dict(
                title='Date',
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title='Comment',
                linecolor="#BCCCDC",  # Sets color of Y-axis line
                showgrid=False,  # Removes Y-axis grid lines
            )
        )

        layout_share = go.Layout(
            plot_bgcolor="#FFF",  # Sets background color to white
            xaxis=dict(
                title="Date",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title='Share',
                linecolor="#BCCCDC",  # Sets color of Y-axis line
                showgrid=False,  # Removes Y-axis grid lines
            )
        )

        fig_react = go.Figure(go.Scatter(x=df["Date"], y=df["React"]),layout=layout_react)
        fig_comment = go.Figure(go.Scatter(x=df["Date"], y=df["Comment"]),layout=layout_comment)
        fig_share = go.Figure(go.Scatter(x=df["Date"], y=df["Share"]),layout=layout_share)

        return fig_react, fig_comment, fig_share

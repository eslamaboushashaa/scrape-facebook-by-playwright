import streamlit as st
from facebook_backend import parse_facebook
parse_facebook_url = parse_facebook()
st.set_page_config('Facebook scraper app', layout='wide')
st.markdown("""

### **This app will help you to compare your page or company page with your competitors' page.**

**This app helps you to understand the performance of any Facebook page, in future, this app will help you in any social media platform.**
                
*All results will show in graphs to make understanding is easy*
""")
st.title('Facebook scraper')
st.markdown("""
>*By [Eslam Abou-shashaa](https://eslam.tech/)* :wave: 

*If you want to connect me, I will be glad to have a conversation with you.*
<a href="https://www.linkedin.com/in/eslamaboushashaa/">
  <img align="middle" alt="Linkedin" width="22px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg" />
</a> 
""",unsafe_allow_html=True)
st.info('All you need to do is put the URL')

with st.form(key="form"):
    page_url = st.text_input("Put page link.")
    st.text(f"(Example: https://www.facebook.com/eslamaboushashaa)")

    submit_button = st.form_submit_button(label='Scrape Facebook page')

    if submit_button:
        st.balloons()
        with st.spinner("Please wait for a minute, Scraping time..."):
            html = parse_facebook_url.go_to_page(page_url)
            date, Reacts ,no_comment , no_share = parse_facebook_url.extract_data(html)

            df = parse_facebook_url.clean_and_create_DF(date, Reacts, no_comment, no_share)

            react_line, comment_line, share_line = parse_facebook_url.visualise_data(df)
            st.dataframe(df)
            col1, col2, coldummy = st.columns(3)
            col1.metric('Number of posts',len(df))
            col2.metric('Number of all Reacts',df['React'].sum())
            col3, col4, coldummy2 = st.columns(3)
            col3.metric('Number of all Comments', df['Comment'].sum())
            col4.metric('Number of all Shares',df['Share'].sum())
            col5, col6, col7 = st.columns(3)
            col5.metric('Maximum Reacts', df['React'].max())
            col6.metric('Maximum Shares', df['Share'].max())
            col7.metric('Maximum Comments', df['Comment'].max())
            with st.expander('this section for if you want to download this data'):

                dowload_link = parse_facebook_url.download_data_csv(df,'scrape facebook.csv','Click here to download your data!')
                st.markdown(dowload_link, unsafe_allow_html=True)

            with st.expander('See React Visualizations'):
                st.plotly_chart(react_line)
            with st.expander('See comment Visualizations'):
                st.plotly_chart(comment_line)
            with st.expander('See Share Visualizations'):
                st.plotly_chart(share_line)


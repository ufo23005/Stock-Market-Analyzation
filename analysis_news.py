from openai import OpenAI, OpenAIError
from Fetch_News import NewsScraper

class AIAnalysis:
    @staticmethod
    def get_reply(messages):
        '''
        取得分析內容

        Parameters:
        - messages: 傳送給API的資訊 (system_msg, report_example, news_msg)

        Returns:
        - 回傳分析內容
        '''
        client = OpenAI(api_key = "")

        try:
            response = client.chat.completions.create(
                model = 'gpt-4o-mini',
                messages = messages
            )

            reply = response.choices[0].message.content
            # 檢查 token的使用量
            # print(f"\
            #         ChatGPT使用量:\n\
            #         completion_tokens = {response.usage.completion_tokens}\n\
            #         prompt_tokens = {response.usage.prompt_tokens}\n\
            #         total_tokens = {response.usage.total_tokens}")

        except OpenAIError as e:
            reply = f"發生{e.type} 錯誤\n{e.message}"

        return reply
    
    def ai_helper(news_msg):
        '''
        設定角色、輸出內容、輸出格式，使用者輸入

        Parameters:
        - news_msg: 新聞資料

        Returns:
        - list (system_msg, report_example, news_msg)
        '''

        if not news_msg or news_msg.strip() == "":
            return "未提供新聞內容，無法進行分析。"
        
        system_msg = '''
You are a financial news analyst specializing in cryptocurrency, Taiwan stocks, U.S. stocks, forex, ETFs, and other financial markets. Based on the provided news, perform the following analysis:

1. Market Sentiment Score (0-100):
    - High score: Greedy/Optimistic.
    - Low score: Fearful/Pessimistic.

2. Summarize the news in 50 words or fewer:
    - Use Traditional Chinese if the input is Chinese; otherwise, use English.

3. Mentioned Assets:
    List all financial assets mentioned, e.g., 2330 TSMC, TSLA, BTC, 00940. If none, respond with "No".

4. Domain Classification:
    - Cryptocurrency, Taiwan Stocks, U.S. Stocks, Forex, ETF, Other Domains.

5. Trading Recommendation:
    - Suitable for Long
    - Suitable for Short
    - Not Recommended for Trading
Rules:
    Follow all steps strictly.
    Exclude unrelated content.
    If no news is provided, analysis cannot proceed.
'''

        report_example = '''
1. Market Sentiment Score: 80

2. News Summary: (content)。

3. Mentioned Asset Identification: No

4. Domain Classification: Other Domains

5. Trading Recommendation: Not Recommended for Trading
'''
        
        msg =[{
            "role": "system",
            "content": system_msg
        }, {
            "role": "assistant",
            "content":f"{report_example}"
        }, {
            "role": "user",
            "content": (news_msg)
        }]

        reply = AIAnalysis.get_reply(msg)

        return reply
    
if __name__ == "__main__":
    '''
    分析出來的格式
    1. Market Sentiment Score
    2. News Summary
    3. Mentioned Assets
    4. Domain Classification
    5. Trading Recommendation

    須自己拆解文字
    '''
    scraper = NewsScraper()
    news_data = scraper.Followin_Breaking_News()
    news_url = [url['Url'] for url in news_data]
    for url in news_url:
        print('-' * 50)
        result = AIAnalysis.ai_helper(url)
        print(result)
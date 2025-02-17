from langchain_core.prompts import PromptTemplate

tweet_classification_prompt = PromptTemplate(
    input_variables=["tokens", "tweet_text"],
    template="""You are a helpful assistant that determines the sentiment of tweets towards Solana contract addresses or tickers.

For each $TICKER or contract address given here in 'TOKENS:', please output your thoughts analyzing whether the text in 'FULL_TWEET_TEXT:' tweets sentiment (ie is the tweet) is positive, negative, or neutral toward that token.

TOKENS: [{tokens}]

FULL_TWEET_TEXT: {tweet_text}


Schema for output:
{parsing_model}
""",
)

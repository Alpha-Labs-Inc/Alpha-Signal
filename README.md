<h1 align="center">
  <a href="https://alphasignalcrypto.com/">
  <img src="./ui/public/Alpha_signal_circle.png" alt="Alpha Signal Crypto Logo" width="200"/>
  </a>
  <p>
Alpha Signal Crypto
</p>
<br>
  <a href="https://www.python.org/downloads/release/python-3131/">
      <img src="https://img.shields.io/badge/Python-3.13.1-blue.svg" alt="Python Version"/>
  </a>
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/Poetry-2.0.1-blue.svg" alt="Poetry Version"/>
  </a>
  <a href="https://nodejs.org/en/blog/release/v22.13.1">
    <img src="https://img.shields.io/badge/Node.js-22.13.1-blue.svg" alt="Node.js Version"/>
  </a>
  <a href="https://pnpm.io/">
    <img src="https://img.shields.io/badge/pnpm-10.1.0-blue.svg" alt="pnpm Version"/>
  </a>
  <a href="https://github.com/Alpha-Labs-Inc/Alpha-Signal/stargazers">
    <img src="https://img.shields.io/github/stars/Alpha-Labs-Inc/Alpha-Signal?style=social" alt="GitHub Stars"/>
  </a>
<!--   <a href="https://github.com/Alpha-Labs-Inc/Alpha-Signal/releases">
    <img src="https://img.shields.io/github/downloads/Alpha-Labs-Inc/Alpha-Signal/total?color=blue" alt="Downloads"/>
  </a> -->

</br>
</p>

<div align="center">

[😸 Github](https://github.com/Alpha-Labs-Inc/Alpha-Signal)
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
[🌎 Website](https://alphasignalcrypto.com/)
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
[🔔 X](https://x.com/_AlphaSignal_)

</div>
<div align="center">
  
[🚗 Roadmap](https://alphasignalcrypto.com/roadmap)
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
[👀 Vision](https://alphasignalcrypto.com/vision)


</div>

</h1>
<div align="center">

<h4>CA: 3AdCHhGH84c2zr8U8eXaspPbKiPmQgKcqmQtApnSpump</h4>
<br>
</div>

<p>
    
</p>
Alpha Signal Crypto is a cutting-edge platform designed to provide real-time crypto signals, analytics, and market insights to traders and investors. Our mission is to empower users with actionable intelligence, leveraging advanced algorithms and expert analysis to help navigate the fast-paced world of cryptocurrency trading.

## Vision

Alpha Signal Crypto envisions a future where traders and investors have seamless access to accurate, real-time market insights, enabling them to make informed decisions with confidence. Our goal is to democratize crypto trading intelligence by leveraging cutting-edge technology, automation, and expert-driven analysis.

Learn more about our vision and long-term goals: [Alpha Signal Crypto Vision](https://alphasignalcrypto.com/vision)


## Features

- **Real-time Crypto Signals** – Get timely trading signals based on technical and market analysis.
- **Market Analytics** – In-depth insights and trends to help make informed trading decisions.
- **Automated Alerts** – Never miss an opportunity with instant notifications.
- **Automated Selling** - Ensure you never lose - enable auto-selling to get out while it's hot.
- **User-friendly Dashboard** – Intuitive and responsive interface for seamless experience.

## Getting Started

1. **Visit the Website** – [Alpha Signal Crypto](https://alphasignalcrypto.com/)
2. **Explore Features** – Utilize analytics tools and automated alerts to optimize your trades.
3. **Join the Community** – Engage with like-minded traders and stay ahead of the market.

### Setting up your personal crypto management
1. Install `python 3.13.1`
2. Install `poetry 2.0.1`
3. Install `node 22.13.1` and `pnpm 10.1.0`

#### Configuring the backend
The twitter/X api cost to get real time webhooks is nontrivial ($>2000 a month). The best workaround is using a service that resells webhook capability though a third party service. Here is the best available. https://monitor.tweet-catcher.com/.

#### Running the Backend
1. Run `poetry install`
2. Run the main backend: `poetry run python -m alphasignal.app`
   - Your backend is up and running for signals.
3. In a new terminal window, run the order processor service: `poetry run python -m alphasignal.processor`
4. In another terminal, run the ngrok service to forward tweet webhooks: `poetry run python -m alphasignal.ngrok_run`

Note: A single startup script using Docker Compose is in the works to streamline these processes.
#### Running the Frontend
1. In terminal, `cd` to the `ui` folder
2. Run `pnpm install`
3. Run `npm run dev`
4. Click on the local-host link, you now have access to view your Alpha Signal application.


## Integrations

- Frontend: React
- Backend: Python
- Package Management: Poetry
- Database: A locally hosted SQLite Database.
- Integrations: Jupiter, Dex Screener, X/Twitter
## Integrations
| Category          | Integration                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| Core Application  | <a href="https://react.dev/"><img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" alt="React" width="80" style="margin: 20px;" align="top"/></a> <a href="https://www.python.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" alt="Python" width="80" style="margin: 20px;" align="top"/></a> <a href="https://python-poetry.org/"><img src="https://python-poetry.org/images/logo-origami.svg" alt="Poetry" width="60" style="margin: 20px;" align="top"/></a> |
| Database          | <a href="https://www.sqlite.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/3/38/SQLite370.svg" alt="SQLite" width="150" style="margin: 20px;" align="top"/></a> |
| External          | <a href="https://jup.ag/"><img src="https://jup.ag/_next/image?url=%2Fsvg%2Fjupiter-logo.png&w=96&q=75" alt="Jupiter" width="80" style="margin: 20px;" align="top"/></a> <a href="https://x.com/home"><img src="https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg" alt="X" width="80" style="margin: 20px;" align="top"/></a> <a href="https://dexscreener.com/"><img src="https://mediaresource.sfo2.digitaloceanspaces.com/wp-content/uploads/2024/04/20232343/dex-screener-logo-png_seeklogo-527276.png" alt="Dex Screener" width="80" style="margin: 20px;" align="top"/></a> |
| AI Providers      | <a href="https://openai.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/OpenAI_logo_2025_%28symbol%29.svg/640px-OpenAI_logo_2025_%28symbol%29.svg.png" alt="OpenAI" width="60" style="margin: 20px;" align="top"/></a> <a href="https://www.anthropic.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Claude_AI_logo.svg" alt="Anthropic" width="200" style="margin: 20px;" align="top"/></a> <a href="https://deepseek.ai/"><img src="https://upload.wikimedia.org/wikipedia/commons/e/ec/DeepSeek_logo.svg" alt="Deepseek" width="200" style="margin: 20px;" align="top"/></a> <a href="https://ai.google/"><img src="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" alt="Google" width="150" style="margin: 20px;" align="top"/></a> <a href="https://huggingface.co/"><img src="https://upload.wikimedia.org/wikipedia/commons/d/d6/Hf-logo-with-title.svg" alt="HuggingFace" width="250" style="margin: 20px;" align="top"/></a> <a href="https://mistral.ai/"><img src="https://upload.wikimedia.org/wikipedia/commons/e/e6/Mistral_AI_logo_%282025%E2%80%93%29.svg" alt="Mistral" width="100" style="margin: 20px;" align="top"/></a> |


## Roadmap

Our roadmap outlines the future development and enhancements of Alpha Signal Crypto. We are committed to continuously improving our platform by introducing new features, refining our analytics, and expanding market coverage. Key milestones include AI-powered trading insights, enhanced automation tools, and a more intuitive user experience.

Check out our roadmap to see upcoming features and developments: [Alpha Signal Crypto Roadmap](https://alphasignalcrypto.com/roadmap)


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Ngrok Networking Setup

When you start the system with `docker-compose up --build` the ngrok service will forward your internal port 8000 to a public URL. You will see an output like:

    Ingress established at http://<random-id>.ngrok.io

Use this URL to configure any external services (e.g. webhooks) that need to reach your application. If required, update the `API_URL` environment variable in the docker-compose file or your application configuration with this URL.

Stay ahead in the crypto game with Alpha Signal Crypto 🚀

import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en" className="dark">
      <Head>
        <meta charSet="utf-8" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.0.3/dist/fonts/geist-sans/style.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.0.3/dist/fonts/geist-mono/style.css" />
      </Head>
      <body className="bg-[#09090b] text-[#ededed] font-sans antialiased selection:bg-white/10 selection:text-white">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

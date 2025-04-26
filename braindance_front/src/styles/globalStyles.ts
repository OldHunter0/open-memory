import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    background: #0a0a0a;
    color: #00ff9d;
    font-family: 'Orbitron', sans-serif;
    overflow: hidden;
  }

  ::-webkit-scrollbar {
    width: 8px;
    background: #1a1a1a;
  }

  ::-webkit-scrollbar-thumb {
    background: #00ff9d;
    border-radius: 4px;
  }
`;
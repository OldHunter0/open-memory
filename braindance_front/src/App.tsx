import { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyle } from './styles/globalStyles';
import { cyberTheme } from './styles/theme';
import { CyberBackground, GridLines } from './components/CyberBackground';
import { NeonText } from './components/NeonText';
import { MemoryButton } from './components/MemoryButton';
import { ChatWindow } from './components/ChatWindow';
// import { motion } from 'framer-motion';
import styled from 'styled-components';
import { memoryService } from './api/memoryService';


const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  width: 100%;
  box-sizing: border-box;
`;

const ControlPanel = styled.div`
  display: flex;
  gap: 2rem;
  margin: 2rem 0;
`;

const StatusMessage = styled.div`
  color: ${({ theme }) => theme.colors.primary};
  font-family: ${({ theme }) => theme.fonts.secondary};
  margin-top: 1rem;
  min-height: 1.5rem;
`;

export default function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  // Handle memory download
  const handleDownloadMemory = async () => {
    setIsDownloading(true);
    setStatusMessage('Exporting memory...');

    try {
      const fileName = await memoryService.exportMemory();
      setStatusMessage(`Memory exported: ${fileName}`);
    } catch (error) {
      setStatusMessage(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Handle memory upload
  const handleUploadMemory = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || event.target.files.length === 0) return;

    const file = event.target.files[0];
    setIsUploading(true);
    setStatusMessage(`Uploading memory: ${file.name}...`);

    try {
      await memoryService.importMemory(file);
      setStatusMessage(`Memory successfully imported`);
    } catch (error) {
      setStatusMessage(`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (event.target) event.target.value = '';
    }
  };

  return (
    <ThemeProvider theme={cyberTheme}>
      <GlobalStyle />
      <CyberBackground />
      <GridLines />

      <AppContainer>
        <NeonText style={{ fontSize: '3rem', marginBottom: '2rem' }}>
          BRAIN DANCE v2.0.77
        </NeonText>

        <ControlPanel>
          <MemoryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDownloadMemory}
            disabled={isDownloading}
          >
            {isDownloading ? 'Downloading...' : 'Download Memory'}
          </MemoryButton>
          <MemoryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => document.getElementById('memory-upload')?.click()}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Load Memory'}
          </MemoryButton>
          <input
            id="memory-upload"
            type="file"
            hidden
            accept=".snapshot"
            onChange={handleUploadMemory}
          />
        </ControlPanel>

        <StatusMessage>{statusMessage}</StatusMessage>

        <ChatWindow />
      </AppContainer>
    </ThemeProvider>
  );
}
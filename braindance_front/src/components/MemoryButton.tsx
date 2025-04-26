import styled from 'styled-components';
import { motion } from 'framer-motion';

export const MemoryButton = styled(motion.button)`
  padding: 15px 30px;
  background: transparent;
  border: 2px solid ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.primary};
  font-family: ${({ theme }) => theme.fonts.secondary};
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 0;
    height: 0;
    background: rgba(0, 255, 157, 0.1);
    border-radius: 50%;
    transition: all 0.5s ease;
  }

  &:hover {
    box-shadow: 0 0 20px ${({ theme }) => theme.colors.primary};
    
    &::before {
      width: 300px;
      height: 300px;
    }
  }

  &:active {
    transform: scale(0.95);
  }
`;
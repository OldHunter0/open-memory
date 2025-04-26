import styled from 'styled-components';
import { motion } from 'framer-motion';

export const CyberBackground = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    45deg,
    ${({ theme }) => theme.colors.background} 0%,
    #1a1a1a 100%
  );
  z-index: -1;

  &::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 255, 157, 0.1) 0px,
      rgba(0, 255, 157, 0.1) 1px,
      transparent 1px,
      transparent 10px
    );
    opacity: 0.3;
  }
`;

export const GridLines = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(to right, rgba(0, 255, 157, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 255, 157, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
`;
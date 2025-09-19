import {
  AddCircleOutline,
  DescriptionOutlined,
  Facebook,
  Storage,
  Language,
  PsychologyOutlined,
  LinkedIn,
  Link,
  Search,
  Calculate,
  Build as GenericToolIcon,
  MusicNote, // Placeholder for TikTok
} from '@mui/icons-material';
import { JSX } from 'react';

const iconMapping: { [key: string]: JSX.Element } = {
  add: <AddCircleOutline sx={{ color: 'grey.600' }} />,
  create: <AddCircleOutline sx={{ color: 'grey.600' }} />,
  file: <DescriptionOutlined sx={{ color: 'grey.600' }} />,
  document: <DescriptionOutlined sx={{ color: 'grey.600' }} />,
  facebook: <Facebook sx={{ color: 'grey.600' }} />,
  database: <Storage sx={{ color: 'grey.600' }} />,
  storage: <Storage sx={{ color: 'grey.600' }} />,
  internet: <Language sx={{ color: 'grey.600' }} />,
  knowledge: <PsychologyOutlined sx={{ color: 'grey.600' }} />,
  linkedin: <LinkedIn sx={{ color: 'grey.600' }} />,
  link: <Link sx={{ color: 'grey.600' }} />,
  search: <Search sx={{ color: 'grey.600' }} />,
  calculator: <Calculate sx={{ color: 'grey.600' }} />,
  tiktok: <MusicNote sx={{ color: 'grey.600' }} />, // Placeholder
};

export const getToolIcon = (toolName: string): JSX.Element => {
  // DEBUG: Log the tool name to see what we're receiving from the history
  console.log('getToolIcon received toolName:', toolName);

  if (!toolName) {
    return <GenericToolIcon sx={{ color: 'grey.600' }} />;
  }
  const lowerToolName = toolName.toLowerCase();
  // Revert to `includes` for more flexible matching (e.g., 'calculator_tool' includes 'calculator')
  const matchingKey = Object.keys(iconMapping).find(key => lowerToolName.includes(key));

  return matchingKey ? iconMapping[matchingKey] : <GenericToolIcon sx={{ color: 'grey.600' }} />;
};

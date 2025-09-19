'use client';

import { 
  Accordion, 
  AccordionSummary, 
  AccordionDetails, 
  Typography, 
  Stack, 
  Box 
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  AutoAwesome as SparklesIcon,
} from '@mui/icons-material';
import { FunctionCall } from '@/libs/types';
import { getToolIcon } from '@/libs/utils/toolIcons';

interface ThinkingDisplayProps {
  steps: FunctionCall[];
}

export default function ThinkingDisplay({ steps }: ThinkingDisplayProps) {
  if (!steps || steps.length === 0) return null;
console.log('ThinkingDisplay received steps:', steps);
  return (
    <Box sx={{ width: '100%', mb: 1 }}>
      <Accordion 
        elevation={0} 
        sx={{ 
          border: 1, 
          borderColor: 'divider', 
          borderRadius: 2,
          '&:before': { display: 'none' }
        }}
      >
        <AccordionSummary 
          expandIcon={<ExpandMoreIcon />}
          sx={{ flexDirection: 'row-reverse', '& .MuiAccordionSummary-content': { ml: 1 } }}
        >
          <Stack direction="row" spacing={1} alignItems="center">
            <SparklesIcon fontSize="small" color="primary" />
            <Typography variant="body2" fontWeight="medium">
              {steps.length > 1 ? `${steps.length} tools is calling` : '1 tool is calling'}
            </Typography>
          </Stack>
        </AccordionSummary>
        <AccordionDetails sx={{ pt: 0 }}>
          <Stack spacing={2}>
            {steps.map((step, index) => (
              <Stack key={index} direction="row" spacing={1.5} alignItems="flex-start">
                {getToolIcon(step.name || step.function_name)}
                <Stack>
                  <Typography variant="body2">
                    <Box component="span" fontWeight="bold">{step.name || step.function_name}</Box>
                    <Box component="span" sx={{ color: 'text.secondary', ml: 0.5 }}>
                      | {step.args?.action_description}
                    </Box>
                  </Typography>
                  {step.args?.expected_outcome && (
                    <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                      Expect: {step.args.expected_outcome}
                    </Typography>
                  )}
                </Stack>
              </Stack>
            ))}
          </Stack>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}

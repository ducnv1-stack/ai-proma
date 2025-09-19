export type MessageType = 'text' | 'json' | 'markdown' | 'table';

export interface ParsedMessage {
  type: MessageType;
  content: any;
  metadata?: Record<string, any>;
}

// Cố gắng parse JSON một cách an toàn
const tryParseJson = (text: string): any | null => {
  try {
    // Loại bỏ các ký tự ```json` ở đầu và ``` ở cuối nếu có
    const cleanedText = text.trim().replace(/^```json\n|\n```$|```$/g, '').trim();
    const data = JSON.parse(cleanedText);
    // Chỉ chấp nhận object hoặc array, không chấp nhận chuỗi, số, boolean đơn thuần
    if (typeof data === 'object' && data !== null) {
      return data;
    }
    return null;
  } catch (e) {
    return null;
  }
};

// Kiểm tra xem có phải là Markdown table không
const isMarkdownTable = (text: string): boolean => {
  const lines = text.trim().split('\n');
  if (lines.length < 2) return false;
  // Dòng thứ hai phải là dòng phân cách của table (chứa --- | ---)
  const separatorLine = lines[1].trim();
  return separatorLine.includes('|') && separatorLine.includes('-');
};

// Kiểm tra các dấu hiệu của Markdown
const isMarkdown = (text: string): boolean => {
  // Dấu hiệu: headings, lists, bold, italic, code blocks
  const markdownRegex = /(^#{1,6}\s)|(^\s*[-*+]\s)|(\*\*.*?\*\*)|(_.*?_)|(```)/;
  return markdownRegex.test(text);
};


export const parseMessageContent = (text: string): ParsedMessage => {
  const jsonContent = tryParseJson(text);
  if (jsonContent) {
    return {
      type: 'json',
      content: jsonContent,
    };
  }

  if (isMarkdownTable(text)) {
    return {
      type: 'table',
      content: text, // Table renderer sẽ parse chi tiết sau
    };
  }

  if (isMarkdown(text)) {
    return {
      type: 'markdown',
      content: text,
    };
  }

  return {
    type: 'text',
    content: text,
  };
};

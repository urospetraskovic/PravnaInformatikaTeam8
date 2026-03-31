const path = require('path');
const fs = require('fs');
const { DOMParser } = require('@xmldom/xmldom');

function parseGlava23(glava23Path) {
  if (!fs.existsSync(glava23Path)) {
    return { error: 'Glava 23 file not found', status: 404 };
  }

  const xmlContent = fs.readFileSync(glava23Path, 'utf8');
  const parser = new DOMParser();
  const doc = parser.parseFromString(xmlContent);

  // Extract all articles from the XML
  const articles = [];
  const articleElements = doc.getElementsByTagNameNS('*', 'article');

  for (let i = 0; i < articleElements.length; i++) {
    const article = articleElements[i];
    const eId = article.getAttribute('eId');
    const numElement = article.getElementsByTagNameNS('*', 'num')[0];
    const articleNum = numElement?.textContent || '';
    const heading = article.getElementsByTagNameNS('*', 'heading')[0]?.textContent || 'Nepoznat';
    const paragraphs = article.getElementsByTagNameNS('*', 'paragraph');
    const content = [];
    const paragraphItems = [];

    for (let j = 0; j < paragraphs.length; j++) {
      const paragraph = paragraphs[j];
      const paraNum = paragraph.getElementsByTagNameNS('*', 'num')[0]?.textContent?.trim() || '';
      const pNodes = paragraph.getElementsByTagNameNS('*', 'p');
      const paraId = paragraph.getAttribute('eId') || (eId ? `${eId}__para_${j + 1}` : `para_${j + 1}`);

      if (pNodes.length > 0) {
        const paraTextParts = [];
        for (let k = 0; k < pNodes.length; k++) {
          const text = (pNodes[k].textContent || '').trim();
          if (text) {
            paraTextParts.push(text);
            content.push(paraNum ? `${paraNum} ${text}` : text);
          }
        }
        const paraText = paraTextParts.join(' ').trim();
        if (paraText) {
          paragraphItems.push({ eId: paraId, num: paraNum, text: paraText });
        }
        continue;
      }

      // Fallback for paragraphs that do not use explicit <p> nodes.
      const rawText = (paragraph.textContent || '').trim();
      if (rawText) {
        content.push(rawText);
        paragraphItems.push({ eId: paraId, num: paraNum, text: rawText });
      }
    }

    articles.push({
      eId: eId,
      num: articleNum,
      heading: heading,
      paragraphs: paragraphItems,
      content: content.join('\n\n')
    });
  }

  return { articles };
}

module.exports = { parseGlava23 };

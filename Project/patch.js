const fs = require('fs');

const extractArticleTargetNew = `
    function extractArticleTarget(articleText) {
      const text = String(articleText || '').trim();
      if (!text) return null;

      let articleNum = null;
      let paragraphNum = null;

      const dotMatch = text.match(/\\b(258|260)\\.(\\d{1,2})\\b/);
      if (dotMatch) {
        articleNum = dotMatch[1];
        paragraphNum = dotMatch[2];
      }

      if (!articleNum) {
        const explicitArticleMatch = text.match(/(?:čl\\.?|cl\\.?|član|clan)\\s*(\\d{2,3})/i);
        articleNum = explicitArticleMatch ? explicitArticleMatch[1] : null;
      }

      if (!articleNum) {
        const fallbackArticleMatch = text.match(/\\b(258|260)\\b/);
        if (fallbackArticleMatch) articleNum = fallbackArticleMatch[1];
      }

      if (!articleNum) return null;

      if (!paragraphNum) {
        const explicitParagraphMatch = text.match(/(?:st\\.?|stav)\\s*(\\d{1,2})/i);
        if (explicitParagraphMatch) {
          paragraphNum = explicitParagraphMatch[1];
        }
      }

      if (!paragraphNum) {
        const brokenPatternMatch = text.match(/\\b(258|260)\\b[^\\d]{0,12}(?:st\\.?|stav)\\s*(\\d{1,2})/i);
        if (brokenPatternMatch) {
          paragraphNum = brokenPatternMatch[2];
        }
      }

      if (!paragraphNum) {
        const numbers = (text.match(/\\d+/g) || []).map((n) => parseInt(n, 10));
        if (numbers.length >= 2 && (numbers[0] === 258 || numbers[0] === 260) && numbers[1] > 0 && numbers[1] <= 10) {
          paragraphNum = String(numbers[1]);
        }
      }

      const label = paragraphNum ? \`\${articleNum}.\${paragraphNum}\` : \`\${articleNum}\`;
      return {
        articleNum,
        paragraphNum,
        hash: paragraphNum ? \`#art_\${articleNum}__para_\${paragraphNum}\` : \`#art_\${articleNum}\`,
        label
      };
    }
`;

try {
  let content = fs.readFileSync('web/public/index.html', 'utf8');
  let tempFunc = fs.readFileSync('temp_func.txt', 'utf8');
  // Strip empty lines to make matching easier or use string replacement.
  
  // Actually, replace using regex or index
  const startIdx = content.indexOf('    function extractArticleTarget(articleText) {');
  if (startIdx === -1) throw new Error("Could not find start index");
  
  const endIdx = content.indexOf('    function navigateToArticleFromEvent(event, articleNum, paragraphNum = null) {');
  if (endIdx === -1) throw new Error("Could not find end index");

  const newContent = content.substring(0, startIdx) + extractArticleTargetNew + '\n' + content.substring(endIdx);
  fs.writeFileSync('web/public/index.html', newContent, 'utf8');
  console.log("Successfully replaced extractArticleTarget in index.html");
} catch(err) {
  console.error("Error: ", err);
}

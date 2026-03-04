function inlineFormat(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**"))
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    return part;
  });
}

export default function MarkdownRenderer({ text }) {
  const lines = text.split("\n");
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Table
    if (line.trim().startsWith("|") && lines[i + 1]?.trim().match(/^\|[-| :]+\|$/)) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const headers = tableLines[0].split("|").filter(c => c.trim() !== "");
      const rows    = tableLines.slice(2).map(r => r.split("|").filter(c => c.trim() !== ""));
      elements.push(
        <div key={`t${i}`} className="md-table-wrapper">
          <table className="md-table">
            <thead><tr>{headers.map((h, j) => <th key={j}>{inlineFormat(h.trim())}</th>)}</tr></thead>
            <tbody>{rows.map((row, j) => (
              <tr key={j}>{row.map((cell, k) => <td key={k}>{inlineFormat(cell.trim())}</td>)}</tr>
            ))}</tbody>
          </table>
        </div>
      );
      continue;
    }

    // Headings
    if (line.startsWith("### ")) { elements.push(<h4 key={i} className="md-h3">{inlineFormat(line.slice(4))}</h4>); i++; continue; }
    if (line.startsWith("## "))  { elements.push(<h3 key={i} className="md-h2">{inlineFormat(line.slice(3))}</h3>); i++; continue; }
    if (line.startsWith("# "))   { elements.push(<h2 key={i} className="md-h1">{inlineFormat(line.slice(2))}</h2>); i++; continue; }

    // Numbered list
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(<li key={i}>{inlineFormat(lines[i].replace(/^\d+\.\s/, ""))}</li>);
        i++;
      }
      elements.push(<ol key={`ol${i}`} className="md-ol">{items}</ol>);
      continue;
    }

    // Bullet list
    if (/^[-*]\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^[-*]\s/.test(lines[i])) {
        items.push(<li key={i}>{inlineFormat(lines[i].replace(/^[-*]\s/, ""))}</li>);
        i++;
      }
      elements.push(<ul key={`ul${i}`} className="md-ul">{items}</ul>);
      continue;
    }

    if (line.trim() === "") { i++; continue; }

    elements.push(<p key={i} className="md-p">{inlineFormat(line)}</p>);
    i++;
  }

  return <div className="md-body">{elements}</div>;
}

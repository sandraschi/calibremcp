import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const mdComponents = {
  h2: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
    const text = String(children ?? '');
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-');
    return (
      <h2
        id={id}
        {...props}
        className="scroll-mt-6 text-xl font-semibold text-slate-100 mt-8 mb-3 first:mt-0"
      >
        {children}
      </h2>
    );
  },
  h3: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
    const text = String(children ?? '');
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-');
    return (
      <h3 id={id} {...props} className="scroll-mt-6 text-base font-semibold text-amber mt-6 mb-2">
        {children}
      </h3>
    );
  },
  p: ({ children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p {...props} className="text-sm leading-relaxed text-slate-300 my-2.5">
      {children}
    </p>
  ),
  ul: ({ children, ...props }: React.HTMLAttributes<HTMLUListElement>) => (
    <ul {...props} className="my-2.5 space-y-1.5">
      {children}
    </ul>
  ),
  ol: ({ children, ...props }: React.HTMLAttributes<HTMLOListElement>) => (
    <ol {...props} className="my-2.5 space-y-1.5 list-decimal list-inside">
      {children}
    </ol>
  ),
  li: ({ children, ...props }: React.HTMLAttributes<HTMLLIElement>) => (
    <li {...props} className="text-sm text-slate-300 leading-relaxed pl-1 marker:text-amber">
      {children}
    </li>
  ),
  a: ({ children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a {...props} className="text-amber hover:underline">
      {children}
    </a>
  ),
  code: ({ children, className, ...props }: React.HTMLAttributes<HTMLElement>) => {
    const inline = !className?.includes('language-');
    if (inline) {
      return (
        <code
          {...props}
          className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-amber-200 text-[0.8em] font-mono whitespace-nowrap"
        >
          {children}
        </code>
      );
    }
    return (
      <code {...props} className="font-mono text-[0.8rem] text-slate-200">
        {children}
      </code>
    );
  },
  pre: ({ children, ...props }: React.HTMLAttributes<HTMLPreElement>) => (
    <pre
      {...props}
      className="my-3 p-4 rounded-lg bg-slate-950 border border-slate-700 overflow-x-auto text-[0.8rem] leading-relaxed"
    >
      {children}
    </pre>
  ),
  table: ({ children, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
    <div className="my-3 overflow-x-auto rounded-lg border border-slate-700">
      <table {...props} className="w-full text-sm">
        {children}
      </table>
    </div>
  ),
  thead: ({ children, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <thead {...props} className="bg-slate-800">
      {children}
    </thead>
  ),
  th: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
    <th
      {...props}
      className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-amber"
    >
      {children}
    </th>
  ),
  td: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
    <td {...props} className="px-3 py-2 text-slate-300 border-t border-slate-700/60 align-top">
      {children}
    </td>
  ),
  strong: ({ children, ...props }: React.HTMLAttributes<HTMLElement>) => (
    <strong {...props} className="font-semibold text-slate-100">
      {children}
    </strong>
  ),
  hr: ({ ...props }: React.HTMLAttributes<HTMLHRElement>) => (
    <hr {...props} className="my-6 border-slate-700" />
  ),
};

/** Render help markdown with the fleet slate/amber theme. Shared by /help and HelpModal. */
export function HelpMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {content.trim()}
    </ReactMarkdown>
  );
}

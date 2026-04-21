interface SubIssueTagProps {
  tag: string;
}

export default function SubIssueTag({ tag }: SubIssueTagProps) {
  return (
    <span className="inline-block bg-pink-50 text-pink-700 border border-pink-200 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide">
      {tag.replace(/_/g, ' ')}
    </span>
  );
}

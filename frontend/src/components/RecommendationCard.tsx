
interface Recommendation {
  company: string;
  reason: string;
  risk: string;
  allocation: string;
  news_sentiment: string;
}

const RecommendationCard: React.FC<{ rec: Recommendation }> = ({ rec }) => (
  <div className="border rounded-lg p-4 my-2 bg-white dark:bg-gray-800 shadow">
    <h3 className="font-bold text-lg">{rec.company}</h3>
    <p className="text-gray-600 dark:text-gray-300 mb-2">{rec.reason}</p>
    <div className="space-y-1 text-sm">
      <div>Risk: <span className="font-semibold">{rec.risk}</span></div>
      <div>Allocation: <span className="font-semibold">{rec.allocation}</span></div>
      <div>News: <span className="italic">{rec.news_sentiment}</span></div>
    </div>
  </div>
);

export default RecommendationCard;

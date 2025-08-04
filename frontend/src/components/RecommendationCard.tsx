import React from 'react';

export default function RecommendationCard({ rec }: { rec: any }) {
  return (
    <div className="border rounded-lg p-4 my-2 bg-white dark:bg-gray-800 shadow">
      <h3 className="font-bold text-lg">{rec.company}</h3>
      <p>{rec.reason}</p>
      <div>Risk: <b>{rec.risk}</b></div>
      <div>Allocation: <b>{rec.allocation}</b></div>
      <div>News: <i>{rec.news_sentiment}</i></div>
    </div>
  );
}

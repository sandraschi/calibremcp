import { SeriesDetailClient } from './series-detail-client';

export function generateStaticParams() {
  return [{ id: '0' }];
}

export default async function SeriesDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <SeriesDetailClient id={id} />;
}

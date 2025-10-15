import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '../services/api'
import { MapPinIcon, CalendarDaysIcon, DocumentTextIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'

const mockProperties = [
  {
    id: 1,
    address: '123 Main St, Austin, TX',
    status: 'In Negotiation',
    value: '$475,000',
    nextAction: 'Review inspection report',
    timeline: [
      { label: 'Offer Received', date: '2025-10-10' },
      { label: 'Inspection', date: '2025-10-14' },
      { label: 'Final Walkthrough', date: '2025-10-20' },
    ],
    matterportUrl: 'https://my.matterport.com/show/?m=example',
  }
]

export default function PropertiesPage() {
  const { data: metrics } = useQuery({
    queryKey: ['property-metrics'],
    queryFn: () => analyticsService.getReports()
  })

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Properties</h1>
        <p className="text-gray-600 mt-2">Track every transaction, document, and conversation by property.</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Active Transactions" value={metrics?.properties?.active || 3} />
        <MetricCard title="Average Days to Close" value={metrics?.properties?.avg_days_to_close || 18} />
        <MetricCard title="Total Volume" value={`$${metrics?.properties?.total_volume || '1.2M'}`} />
      </section>

      <section className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Portfolio Overview</h2>
          <button className="btn-secondary">Add Property</button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Property</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Next Action</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timeline</th>
                <th scope="col" className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockProperties.map((property) => (
                <tr key={property.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary-50 rounded-lg">
                        <MapPinIcon className="h-5 w-5 text-primary-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{property.address}</p>
                        <p className="text-xs text-gray-500">MLS #123456</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-1 text-xs font-medium bg-warning-100 text-warning-700 rounded-full">
                      {property.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{property.value}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{property.nextAction}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <CalendarDaysIcon className="h-4 w-4" />
                      <span>
                        Upcoming: {property.timeline[1].label} on {property.timeline[1].date}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <a href={property.matterportUrl} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700 inline-flex items-center">
                      Matterport tour
                      <ArrowTopRightOnSquareIcon className="h-4 w-4 ml-1" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TimelineCard title="Transaction Timeline" events={mockProperties[0].timeline} />
        <DocumentsCard />
      </section>
    </div>
  )
}

function MetricCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
    </div>
  )
}

function TimelineCard({ title, events }: { title: string; events: { label: string; date: string }[] }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ol className="relative border-l border-gray-200 ml-3 space-y-6">
        {events.map((event, idx) => (
          <li key={event.label} className="ml-6">
            <span className="absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-primary-600">
              {idx + 1}
            </span>
            <p className="text-sm font-medium text-gray-900">{event.label}</p>
            <p className="text-xs text-gray-500">{event.date}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}

function DocumentsCard() {
  const documents = [
    { name: 'Inspection Report.pdf', status: 'Pending Review', uploaded: '2025-10-14', size: '2.3 MB' },
    { name: 'Offer Agreement.pdf', status: 'Signed', uploaded: '2025-10-12', size: '850 KB' },
    { name: 'Appraisal.pdf', status: 'In Progress', uploaded: '2025-10-11', size: '1.1 MB' },
  ]
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents</h3>
      <ul className="space-y-3">
        {documents.map((doc) => (
          <li key={doc.name} className="flex items-center justify-between border border-gray-200 rounded-lg p-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <DocumentTextIcon className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                <p className="text-xs text-gray-500">Uploaded {doc.uploaded} · {doc.size}</p>
              </div>
            </div>
            <span className={`text-xs font-medium ${doc.status === 'Signed' ? 'text-success-600' : doc.status === 'Pending Review' ? 'text-warning-600' : 'text-gray-500'}`}>
              {doc.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}


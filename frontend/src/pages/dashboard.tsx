import type { NextPage } from 'next';

const Dashboard: NextPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        </nav>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Skills Learning', value: '3', color: 'blue' },
            { label: 'Week Streak', value: '7 days', color: 'green' },
            { label: 'Total XP', value: '850', color: 'purple' },
            { label: 'Study Hours', value: '12.5h', color: 'orange' },
          ].map((stat) => (
            <div key={stat.label} className={`bg-${stat.color}-50 rounded-lg p-6`}>
              <p className="text-gray-600 text-sm">{stat.label}</p>
              <p className={`text-3xl font-bold text-${stat.color}-600 mt-2`}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        <section className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">My Skills</h2>
          <p className="text-gray-600">
            Skills list coming soon...
          </p>
        </section>

        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Weekly Study Plan</h2>
          <p className="text-gray-600">
            AI-generated study plan coming soon...
          </p>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;

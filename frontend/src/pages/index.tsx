import type { NextPage } from 'next';
import Link from 'next/link';

const Home: NextPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">VibeDrive</h1>
          <p className="text-gray-600">AI-powered personal learning planner</p>
        </nav>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <section className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Plan your learning journey
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Define skills, track progress, and get AI-powered learning plans
          </p>
          <div className="space-x-4">
            <Link href="/dashboard">
              <button className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700">
                Get Started
              </button>
            </Link>
            <Link href="/login">
              <button className="border-2 border-indigo-600 text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-indigo-50">
                Sign In
              </button>
            </Link>
          </div>
        </section>

        <section className="grid md:grid-cols-3 gap-8 py-12">
          {[
            {
              title: 'Define Skills',
              description: 'Break down your learning goals into manageable skills',
              icon: '📚',
            },
            {
              title: 'Track Progress',
              description: 'Monitor your learning journey with visual dashboards',
              icon: '📊',
            },
            {
              title: 'AI Study Plans',
              description: 'Get personalized study plans generated every week',
              icon: '🤖',
            },
          ].map((feature) => (
            <div key={feature.title} className="bg-white rounded-lg shadow p-6">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>© 2024 VibeDrive. Built with AI and ❤️</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;

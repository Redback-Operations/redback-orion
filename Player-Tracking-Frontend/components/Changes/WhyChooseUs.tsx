"use client";

export default function WhyChooseUs() {
  const features = [
    {
      title: 'Expertise in Sports Tech',
      desc: 'Years of experience in building intelligent tracking systems trusted by professional athletes and coaches.'
    },
    {
      title: 'Cutting-edge Technology',
      desc: 'We leverage AI, machine learning, and pose estimation to deliver real-time actionable insights.'
    },
    {
      title: 'Commitment to Excellence',
      desc: 'We are passionate about driving athletic performance while ensuring player safety and health.'
    }
  ];

  return (
    <section className="py-20 px-6 bg-neutral-900">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Why Choose Us</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
          {features.map((item) => (
            <div key={item.title} className="bg-neutral-800 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-105">
              <h3 className="text-2xl font-extrabold text-yellow-300 mb-4">{item.title}</h3>
              <p className="text-gray-300">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

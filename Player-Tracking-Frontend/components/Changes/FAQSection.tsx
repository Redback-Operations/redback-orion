"use client";

export default function FAQSection() {
  const faqs = [
    {
      question: 'How accurate is your athlete tracking system?',
      answer: 'Our system utilizes advanced AI and pose estimation to deliver real-time insights with 95%+ accuracy, trusted by professional teams.'
    },
    {
      question: 'Can the technology be customized for different sports?',
      answer: 'Absolutely! Our solutions are designed to adapt to various sports including soccer, basketball, tennis, and more.'
    },
    {
      question: 'Is training required to use the system?',
      answer: 'Minimal training is needed. We provide intuitive dashboards and user-friendly interfaces to get you started quickly.'
    }
  ];

  return (
    <section className="py-20 bg-neutral-800">
      <div className="max-w-7xl mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Frequently Asked Questions</h2>
        <div className="space-y-8">
          {faqs.map((faq, idx) => (
            <div key={idx} className="bg-neutral-900 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-105">
              <h3 className="text-2xl font-bold text-yellow-300 mb-4">{faq.question}</h3>
              <p className="text-gray-300">{faq.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

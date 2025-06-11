"use client";

import Image from "next/image";

export default function AwardsSection() {
  const awards = [
    {
      title: 'Best Sports Innovation Award 2024',
      img: 'https://tse3.mm.bing.net/th?id=OIP.VNL8fiQyBYt4s2VRdM9PGQHaEK&pid=Api&P=0&h=180',
      desc: 'Recognized for outstanding contributions to sports technology and performance analytics.'
    },
    {
      title: 'Top AI Solution Provider 2025',
      img: 'https://tse3.mm.bing.net/th?id=OIP.I54iaZIZHV-PmW8B3rK-ZAHaE8&pid=Api&P=0&h=180',
      desc: 'Awarded for leveraging artificial intelligence in athlete tracking and injury prevention.'
    }
  ];

  return (
    <section className="py-20 bg-neutral-900">
      <div className="max-w-7xl mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Awards & Recognition</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {awards.map((award) => (
            <div key={award.title} className="bg-neutral-800 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-105">
              <Image src={award.img} alt={award.title} width={500} height={300} className="rounded-xl mb-6" />
              <h3 className="text-2xl font-extrabold text-yellow-300 mb-4">{award.title}</h3>
              <p className="text-gray-300">{award.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

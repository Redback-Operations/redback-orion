"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button"; 

export default function BlogSection() {
  const posts = [
    {
      title: 'How AI is Changing Athlete Performance',
      img: 'https://tse2.mm.bing.net/th?id=OIP.ctLmSqQia138VDyI4KOs7wHaEK&pid=Api&P=0&h=180',
      desc: 'Explore how artificial intelligence and data science are reshaping training strategies across sports.'
    },
    {
      title: 'Top 5 Injury Prevention Tips for 2025',
      img: 'https://tse1.mm.bing.net/th?id=OIP.3Yw1EPFLR4Bw2eudH0IVsgHaEo&pid=Api&P=0&h=180',
      desc: 'Learn the latest tips and technologies that help athletes stay safe and maximize longevity.'
    }
  ];

  return (
    <section className="py-20 px-6 bg-neutral-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Latest News & Blog</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {posts.map((post) => (
            <div key={post.title} className="bg-neutral-900 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-105">
              <Image src={post.img} alt={post.title} width={500} height={300} className="rounded-xl mb-6" />
              <h3 className="text-2xl font-extrabold text-yellow-300 mb-4">{post.title}</h3>
              <p className="text-gray-300 mb-4">{post.desc}</p>
              <Button variant="outline" className="border-yellow-400 text-yellow-400 px-4 py-2 rounded-full hover:bg-yellow-400 hover:text-black transition">
                Read More
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

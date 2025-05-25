
import type { NextApiRequest, NextApiResponse } from 'next';
import pool from '@/components/feedback-api/db';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { name, email, feedback } = req.body;

    try {
      const result = await pool.query(
        'INSERT INTO feedback (name, email, feedback) VALUES ($1, $2, $3) RETURNING *',
        [name, email, feedback]
      );
      res.status(201).json({ message: 'Saved!', feedback: result.rows[0] });
    } catch (error) {
      console.error('Database error:', error);
      res.status(500).json({ error: 'Something went wrong.' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

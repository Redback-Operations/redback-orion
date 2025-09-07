import { Box, Heading } from '@chakra-ui/react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TRENDS } from '../data/mock'

export default function PerformanceTrends() {
  return (
    <Box>
      <Heading size="sm" mb={3} color="whiteAlpha.800">Score Progression</Heading>
      <Box w="100%" h="300px" bg="surface.100" rounded="xl" border="1px solid" borderColor="whiteAlpha.200" p={2}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={TRENDS}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="COL" stroke="#00B0FF" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="CAR" stroke="#F5C400" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  )
}

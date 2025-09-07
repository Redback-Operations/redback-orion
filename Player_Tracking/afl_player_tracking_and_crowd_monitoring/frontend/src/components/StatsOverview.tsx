import { Box, SimpleGrid, Heading, Text, VStack } from '@chakra-ui/react'

export default function StatsOverview() {
  return (
    <Box>
      <Heading size="sm" mb={3} color="whiteAlpha.800">Stats Overview</Heading>
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
        <StatCard title="Top Player (Live)" value="J. Smith – 18 disposals" />
        <StatCard title="Team Efficiency" value="73% inside-50 conversion" />
        <StatCard title="Heatmap (Preview)" value="Midfield dominance" />
      </SimpleGrid>
    </Box>
  )
}

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <VStack align="start" p={4} bg="blackAlpha.400" rounded="md" border="1px solid" borderColor="whiteAlpha.200" spacing={1}>
      <Text fontSize="xs" color="whiteAlpha.700">{title}</Text>
      <Heading size="md">{value}</Heading>
      <Box w="100%" h="100px" bg="whiteAlpha.200" rounded="sm" />
    </VStack>
  )
}
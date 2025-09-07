import { Box, Flex, Heading, Text, Progress, HStack, VStack, Badge, Image } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { CURRENT_MATCH } from '../data/mock'
const MBox: any = motion(Box)

export default function CurrentMatchCard() {
  const m = CURRENT_MATCH
  const total = m.possession.home + m.possession.away
  const homePct = Math.round((m.possession.home / total) * 100)

  return (
    <MBox p={6} borderWidth="1px" borderColor="whiteAlpha.200" rounded="xl" bg="surface.100"
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }}>
      <Flex align="center" justify="space-between" mb={4}>
        <VStack spacing={0} align="start">
          <Heading size="sm" color="whiteAlpha.800">Current Match</Heading>
          <Text fontSize="xs" color="whiteAlpha.700">Live scoreboard & momentum</Text>
        </VStack>
        <Badge colorScheme="purple">{m.period} • {m.timeLeft}</Badge>
      </Flex>

      <Flex align="center" justify="space-between" gap={8}>
        <TeamScore name={m.home.name} score={m.home.score} logo={m.home.logo} />
        <Heading size="lg">vs</Heading>
        <TeamScore name={m.away.name} score={m.away.score} logo={m.away.logo} />
      </Flex>

      <Box mt={6}>
        <Text fontSize="sm" mb={2}>Possession</Text>
        <Progress value={homePct} size="sm" rounded="sm" />
        <HStack justify="space-between" mt={1} fontSize="xs" color="whiteAlpha.700">
          <Text>{m.home.name} {homePct}%</Text>
          <Text>{100 - homePct}% {m.away.name}</Text>
        </HStack>
      </Box>

      <HStack mt={6} spacing={4}>
        {m.keyStats.map(s => (
          <Box key={s.label} flex="1" p={4} bg="blackAlpha.400" rounded="md"
               border="1px solid" borderColor="whiteAlpha.200">
            <Text fontSize="xs" color="whiteAlpha.700">{s.label}</Text>
            <Heading size="md">{s.value}</Heading>
          </Box>
        ))}
      </HStack>
    </MBox>
  )
}

function TeamScore({ name, score, logo }: { name: string; score: number; logo: string }) {
  return (
    <VStack spacing={1}>
      <Image src={logo} alt={name} w="28px" h="28px" />
      <Text fontSize="sm" color="whiteAlpha.700">{name}</Text>
      <Heading size="2xl">{score}</Heading>
    </VStack>
  )
}

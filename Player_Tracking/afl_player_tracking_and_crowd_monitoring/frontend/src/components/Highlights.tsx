import { Box, Heading, HStack, VStack, Text } from '@chakra-ui/react'
import { HIGHLIGHTS } from '../data/mock'

export default function Highlights() {
  return (
    <Box>
      <Heading size="sm" mb={3} color="whiteAlpha.800">Quick Highlights</Heading>
      <HStack spacing={4} overflowX="auto" py={1}>
        {HIGHLIGHTS.map(h => (
          <Box key={h.id} minW="240px" p={4} bg="blackAlpha.400" rounded="md" border="1px solid" borderColor="whiteAlpha.200" _hover={{ transform: 'translateY(-2px)' }} transition="all .2s">
            <VStack align="start" spacing={1}>
              <Box w="100%" h="120px" bg="whiteAlpha.200" rounded="sm" />
              <Text fontWeight="semibold">{h.title}</Text>
              <Text fontSize="xs" color="whiteAlpha.700">{h.ts}</Text>
            </VStack>
          </Box>
        ))}
      </HStack>
    </Box>
  )
}
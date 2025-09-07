import { Box, Heading, Table, Thead, Tr, Th, Tbody, Td, Badge } from '@chakra-ui/react'
import { FIXTURES } from '../data/mock'

export default function FixturesResults() {
  return (
    <Box>
      <Heading size="sm" mb={3} color="whiteAlpha.800">Fixtures & Results</Heading>
      <Box bg="surface.100" rounded="xl" border="1px solid" borderColor="whiteAlpha.200" p={2}>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr><Th>Date</Th><Th>Opponent</Th><Th>Venue</Th><Th>Status</Th></Tr>
          </Thead>
          <Tbody>
            {FIXTURES.map((f, i) => (
              <Tr key={i}>
                <Td>{f.date}</Td><Td>{f.opponent}</Td><Td>{f.venue}</Td>
                <Td>{f.status === 'UPCOMING'
                  ? <Badge colorScheme="blue">Upcoming</Badge>
                  : <Badge colorScheme={f.status.startsWith('W') ? 'green' : 'red'}>{f.status}</Badge>}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </Box>
  )
}

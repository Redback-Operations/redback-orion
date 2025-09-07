import { Box, Flex, Text, Link } from '@chakra-ui/react'

export default function FooterBar() {
  return (
    <Box as="footer" mt={8} py={6} borderTop="1px solid" borderColor="whiteAlpha.200">
      <Flex justify="space-between" px={2} wrap="wrap" rowGap={2}>
        <Text fontSize="sm" color="whiteAlpha.700">© {new Date().getFullYear()} AFL Analytics (Prototype)</Text>
        <Text fontSize="sm" color="whiteAlpha.700">
          Data sources: <Link href="#" color="blue.300">Sample/mock</Link> • Build {import.meta.env.MODE}
        </Text>
      </Flex>
    </Box>
  )
}
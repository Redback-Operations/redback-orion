import { Box, Flex, Heading, Spacer, HStack, Select, Tag, TagLabel, IconButton, Image } from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'
import { useColorMode } from '@chakra-ui/react'
import useLiveClock from '../hooks/useLiveClock'
import { TEAMS } from '../data/mock'
import { useMemo, useState } from 'react'

export default function HeaderBar() {
  const clock = useLiveClock()
  const { colorMode, toggleColorMode } = useColorMode()
  const [team, setTeam] = useState('COL')
  const [period, setPeriod] = useState('Q3')
  const teamLogo = useMemo(() => TEAMS.find(t=>t.id===team)?.logo, [team])

  return (
    <Box as="header" px={6} py={4} borderBottom="1px solid" borderColor="whiteAlpha.200"
      position="sticky" top={0} zIndex={100}
      bgGradient="linear(to-r, rgba(14,17,22,0.9), rgba(18,22,30,0.9))" backdropFilter="blur(8px)">
      <Flex align="center" gap={4}>
        <Flex align="center" gap={2}>
          <Image src={teamLogo} alt="logo" w="24px" h="24px" />
          <Heading size="md">AFL Analytics</Heading>
        </Flex>
        <Tag variant="subtle" colorScheme="blue"><TagLabel>{clock}</TagLabel></Tag>
        <Spacer />
        <HStack spacing={3}>
          <Select value={team} onChange={(e) => setTeam(e.target.value)} w="200px" size="sm">
            {TEAMS.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </Select>
          <Select value={period} onChange={(e) => setPeriod(e.target.value)} w="140px" size="sm">
            {['Q1','Q2','Q3','Q4','Full Time'].map(p => <option key={p} value={p}>{p}</option>)}
          </Select>
          <IconButton aria-label="toggle color mode" size="sm"
            onClick={toggleColorMode}
            icon={colorMode === 'dark' ? <SunIcon /> : <MoonIcon />} />
        </HStack>
      </Flex>
    </Box>
  )
}

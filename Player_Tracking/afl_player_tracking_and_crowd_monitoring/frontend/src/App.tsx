import { Box, Container, Grid, GridItem } from '@chakra-ui/react'
import HeaderBar from './components/HeaderBar'
import CurrentMatchCard from './components/CurrentMatchCard'
import Highlights from './components/Highlights'
import StatsOverview from './components/StatsOverview'
import PerformanceTrends from './components/PerformanceTrends'
import FixturesResults from './components/FixturesResults'
import FooterBar from './components/FooterBar'

export default function App() {
  return (
    <Box minH="100vh">
      <HeaderBar />
      <Container maxW="7xl" py={6}>
        <Grid templateColumns={{ base: '1fr', lg: '1.2fr 1fr' }} gap={6}>
          <GridItem>
            <CurrentMatchCard />
          </GridItem>
          <GridItem>
            <StatsOverview />
          </GridItem>
        </Grid>

        <Box mt={8}>
          <Highlights />
        </Box>

        <Box mt={8}>
          <PerformanceTrends />
        </Box>

        <Box mt={8}>
          <FixturesResults />
        </Box>

        <FooterBar />
      </Container>
    </Box>
  )
}

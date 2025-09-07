import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
  config: { initialColorMode: 'dark', useSystemColorMode: false },
  fonts: {
    heading: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif',
    body: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif',
  },
  styles: {
    global: {
      'html, body, #root': { height: '100%' },
      body: { bgGradient: 'linear(to-b, #0B0E13, #0E1218)' },
    },
  },
  colors: {
    brand: { 500: '#00B0FF', 600: '#0091DA' },
    surface: { 100: 'rgba(255,255,255,0.04)' }
  },
})
export default theme

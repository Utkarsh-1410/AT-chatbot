/**
 * AstroTamil Customer Care Assistant
 * React Native App Entry Point
 */

import { SafeAreaProvider } from 'react-native-safe-area-context';
import ChatScreen from './src/screens/ChatScreen';

function App() {
  return (
    <SafeAreaProvider>
      <ChatScreen />
    </SafeAreaProvider>
  );
}

export default App;

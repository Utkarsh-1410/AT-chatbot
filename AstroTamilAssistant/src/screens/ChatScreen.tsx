import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  StatusBar,
  Alert,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';

// API Configuration
import { API_BASE_URL } from '../config';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface HumanHandoffData {
  name: string;
  phone: string;
  problem: string;
}

type LanguageCode = 'en' | 'ta';

interface LanguageStrings {
  greeting: string;
  placeholder: string;
  send: string;
  requestHuman: string;
  humanFormTitle: string;
  nameLabel: string;
  phoneLabel: string;
  problemLabel: string;
  submit: string;
  cancel: string;
  error: string;
  connectionError: string;
}

const LANGUAGE_STRINGS: Record<LanguageCode, LanguageStrings> = {
  en: {
    greeting: "Hello! I'm AstroTamil Assistant. How can I help you with your astrologer queries today?",
    placeholder: 'Type your message...',
    send: 'Send',
    requestHuman: 'Request Human Agent',
    humanFormTitle: 'Contact Details',
    nameLabel: 'Your Name',
    phoneLabel: 'Contact Number',
    problemLabel: 'Problem Summary',
    submit: 'Submit',
    cancel: 'Cancel',
    error: 'Sorry, I encountered an error. Please check your connection and try again.',
    connectionError: 'Please make sure the backend server is running on http://10.0.2.2:8000',
  },
  ta: {
    greeting: 'வணக்கம்! நான் ஆஸ்ட்ரோதமிழ் உதவியாளர். உங்கள் ஜோதிட சந்தேகங்களுக்கு எவ்வாறு உதவ முடியும்?',
    placeholder: 'உங்கள் செய்தியை தட்டவும்...',
    send: 'அனுப்பு',
    requestHuman: 'மனித முகவரிடம் கேளுங்கள்',
    humanFormTitle: 'தொடர்பு விவரங்கள்',
    nameLabel: 'உங்கள் பெயர்',
    phoneLabel: 'தொடர்பு எண்',
    problemLabel: 'சிக்கல் சுருக்கம்',
    submit: 'சமர்ப்பிக்கவும்',
    cancel: 'ரத்துசெய்யவும்',
    error: 'மன்னிக்கவும், எனக்கு ஒரு பிழை ஏற்பட்டது. உங்கள் இணைப்பை சரிபார்த்து மீண்டும் முயற்சி செய்யவும்.',
    connectionError: 'பின்புல அளவுக்ோல் http://10.0.2.2:8000 இல் இயங்குகிறது என்பதை உறுதி செய்யவும்',
  },
};

const ChatScreen: React.FC = () => {
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: LANGUAGE_STRINGS.en.greeting,
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [language, setLanguage] = useState<LanguageCode>('en');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showHumanForm, setShowHumanForm] = useState(false);
  const [humanFormData, setHumanFormData] = useState<HumanHandoffData>({
    name: '',
    phone: '',
    problem: '',
  });
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  const flatListRef = useRef<FlatList>(null);
  const strings = LANGUAGE_STRINGS[language];

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      let storedSession = await AsyncStorage.getItem('session_id');
      let storedLanguage = (await AsyncStorage.getItem('language')) as LanguageCode | null;
      
      if (!storedSession) {
        const newSessionId = `astrotamil_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        await AsyncStorage.setItem('session_id', newSessionId);
        storedSession = newSessionId;
      }
      
      if (!storedLanguage) {
        storedLanguage = 'en';
        await AsyncStorage.setItem('language', storedLanguage);
      }
      
      setSessionId(storedSession || '');
      setLanguage(storedLanguage || 'en');
      
      // Load conversation history from backend if session exists
      await loadConversationHistory(storedSession || '', storedLanguage || 'en');
    } catch (error) {
      console.error('Error initializing session:', error);
      // Fallback to greeting message if history load fails
      setMessages([{
        id: '1',
        text: LANGUAGE_STRINGS[language].greeting,
        isUser: false,
        timestamp: new Date(),
      }]);
    }
  };

  const loadConversationHistory = async (sessionId: string, lang: LanguageCode) => {
    setIsLoadingHistory(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/conversation-history/`, {
        params: { session_id: sessionId }
      });

      if (response.data.messages && response.data.messages.length > 0) {
        // Convert backend messages to UI format
        const loadedMessages: Message[] = response.data.messages.map((msg: any) => ({
          id: msg.id,
          text: msg.content,
          isUser: msg.is_user,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(loadedMessages);
      } else {
        // New session - show greeting
        setMessages([{
          id: '1',
          text: LANGUAGE_STRINGS[lang].greeting,
          isUser: false,
          timestamp: new Date(),
        }]);
      }
    } catch (error: any) {
      console.log('No previous history or error loading:', error?.response?.status);
      // Show greeting for new sessions
      setMessages([{
        id: '1',
        text: LANGUAGE_STRINGS[lang].greeting,
        isUser: false,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const startNewChat = async () => {
    Alert.alert(
      'Start New Chat',
      'This will start a new conversation. Your current chat history will be saved and can be accessed later.',
      [
        {
          text: 'Cancel',
          style: 'cancel'
        },
        {
          text: 'Start New',
          onPress: async () => {
            try {
              // Generate new session ID
              const newSessionId = `astrotamil_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
              await AsyncStorage.setItem('session_id', newSessionId);
              setSessionId(newSessionId);
              
              // Reset messages with greeting
              setMessages([{
                id: '1',
                text: LANGUAGE_STRINGS[language].greeting,
                isUser: false,
                timestamp: new Date(),
              }]);
              
              Alert.alert('Success', 'New chat session started!');
            } catch (error) {
              console.error('Error starting new chat:', error);
              Alert.alert('Error', 'Failed to start new chat session');
            }
          }
        }
      ]
    );
  };

  const changeLanguage = async (newLanguage: LanguageCode) => {
    try {
      setLanguage(newLanguage);
      await AsyncStorage.setItem('language', newLanguage);
      
      const newGreeting: Message = {
        id: 'greeting-' + newLanguage,
        text: `Language changed to ${newLanguage === 'en' ? 'English' : 'Tamil'}. ${LANGUAGE_STRINGS[newLanguage].greeting}`,
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, newGreeting]);
      setShowLanguageMenu(false);
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  const sendMessage = async () => {
    const message = inputText.trim();
    if (!message || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      if (!sessionId) {
        await initializeSession();
      }
      const response = await axios.post(`${API_BASE_URL}/chat/`, {
        session_id: sessionId,
        message: message,
        language: language,
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.ai_response,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      if (response.data.response_type === 'collect_human_details') {
        setTimeout(() => {
          setShowHumanForm(true);
        }, 500);
      }

    } catch (error: any) {
      console.error('Error sending message:', error?.response ?? error);

      // show server-provided message when available
      const serverMsg = error?.response?.data?.error || error?.response?.data?.message || null;

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: serverMsg || strings.error,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);

      if (error.response?.status === 500) {
        Alert.alert('Server Error', strings.connectionError);
      } else if (error.response?.status === 400 && serverMsg) {
        // Show bad-request reason
        Alert.alert('Error', serverMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const submitHumanRequest = async () => {
    const { name, phone, problem } = humanFormData;
    
    if (!name.trim() || !phone.trim() || !problem.trim()) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/request-human/`, {
        session_id: sessionId,
        name: name,
        phone: phone,
        problem_summary: problem,
      });

      if (response.data.success) {
        Alert.alert(
          'Success',
          `Your request has been submitted. Reference #: ${response.data.reference_number}\n\nAn agent will contact you within 24 hours.`,
          [
            {
              text: 'OK',
              onPress: () => {
                setShowHumanForm(false);
                setHumanFormData({ name: '', phone: '', problem: '' });
                
                const confirmationMsg: Message = {
                  id: Date.now().toString(),
                  text: `Thank you ${name}! Your request (#${response.data.reference_number}) has been submitted. Our agent will contact you at ${phone}.`,
                  isUser: false,
                  timestamp: new Date(),
                };
                setMessages(prev => [...prev, confirmationMsg]);
              },
            },
          ]
        );
      }
    } catch (error: any) {
      console.error('Error submitting human request:', error);
      Alert.alert('Error', 'Failed to submit request. Please try again.');
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageContainer,
      item.isUser ? styles.userMessageContainer : styles.botMessageContainer
    ]}>
      <View style={[
        styles.messageBubble,
        item.isUser ? styles.userBubble : styles.botBubble
      ]}>
        <Text style={[
          styles.messageText,
          item.isUser ? styles.userMessageText : styles.botMessageText
        ]}>
          {item.text}
        </Text>
      </View>
      <Text style={styles.timestamp}>
        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
    </View>
  );

  const renderHumanForm = () => (
    <View style={styles.humanFormOverlay}>
      <View style={styles.humanFormContainer}>
        <View style={styles.formHeader}>
          <Text style={styles.formTitle}>Contact Human Agent</Text>
          <TouchableOpacity onPress={() => setShowHumanForm(false)}>
            <Icon name="close" size={24} color="#666" />
          </TouchableOpacity>
        </View>
        
        <Text style={styles.formSubtitle}>
          Please provide your details for our agent to contact you:
        </Text>
        
        <TextInput
          style={styles.formInput}
          placeholder="Your Name *"
          value={humanFormData.name}
          onChangeText={(text) => setHumanFormData(prev => ({ ...prev, name: text }))}
          placeholderTextColor="#999"
        />
        
        <TextInput
          style={styles.formInput}
          placeholder="Phone Number *"
          value={humanFormData.phone}
          onChangeText={(text) => setHumanFormData(prev => ({ ...prev, phone: text }))}
          keyboardType="phone-pad"
          placeholderTextColor="#999"
        />
        
        <TextInput
          style={[styles.formInput, styles.problemInput]}
          placeholder="Brief description of your issue *"
          value={humanFormData.problem}
          onChangeText={(text) => setHumanFormData(prev => ({ ...prev, problem: text }))}
          multiline
          numberOfLines={4}
          placeholderTextColor="#999"
        />
        
        <TouchableOpacity
          style={styles.submitButton}
          onPress={submitHumanRequest}
        >
          <Text style={styles.submitButtonText}>Submit Request</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar backgroundColor="#6A11CB" barStyle="light-content" />
      
      
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Icon name="chat" size={28} color="#fff" />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.headerTitle}>AstroTamil Assistant</Text>
            <Text style={styles.sessionIdText}>Session: {sessionId.slice(-8)}</Text>
          </View>
          <View style={styles.sessionBadge}>
            <Text style={styles.sessionText}>Online</Text>
          </View>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.iconButton}
            onPress={startNewChat}
          >
            <Icon name="add" size={24} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.languageButton}
            onPress={() => setShowLanguageMenu(!showLanguageMenu)}
          >
            <Icon name="language" size={24} color="#fff" />
            <Text style={styles.languageButtonText}>{language.toUpperCase()}</Text>
          </TouchableOpacity>
        </View>
        {showLanguageMenu && (
          <View style={styles.languageMenu}>
            <TouchableOpacity
              style={[styles.languageOption, language === 'en' && styles.languageOptionActive]}
              onPress={() => changeLanguage('en')}
            >
              <Text style={styles.languageOptionText}>English</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.languageOption, language === 'ta' && styles.languageOptionActive]}
              onPress={() => changeLanguage('ta')}
            >
              <Text style={styles.languageOptionText}>தமிழ்</Text>
            </TouchableOpacity>
          </View>
        )}
        <Text style={styles.headerSubtitle}>
          Ask me about registration, payments, consultations, and more
        </Text>
      </View>

      {isLoadingHistory ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6A11CB" />
          <Text style={styles.loadingText}>Loading chat history...</Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.messagesList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
          showsVerticalScrollIndicator={false}
        />
      )}

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inputContainer}
      >
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder={strings.placeholder}
          placeholderTextColor="#999"
          multiline
          maxLength={500}
          onSubmitEditing={sendMessage}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!inputText.trim() || isLoading) && styles.sendButtonDisabled
          ]}
          onPress={sendMessage}
          disabled={!inputText.trim() || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Icon name="send" size={22} color="#fff" />
          )}
        </TouchableOpacity>
      </KeyboardAvoidingView>

      {showHumanForm && renderHumanForm()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#6A11CB',
    paddingTop: Platform.OS === 'android' ? 40 : 50,
    paddingBottom: 20,
    paddingHorizontal: 16,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: 8,
  },
  iconButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    padding: 8,
    borderRadius: 20,
  },
  languageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    marginBottom: 8,
  },
  languageButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  languageMenu: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 8,
    overflow: 'hidden',
    position: 'absolute',
    top: 110,
    right: 12,
    zIndex: 100,
  },
  languageOption: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  languageOptionActive: {
    backgroundColor: '#f0f0f0',
  },
  languageOptionText: {
    fontSize: 14,
    color: '#333',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  sessionIdText: {
    fontSize: 11,
    color: '#E0E0E0',
    marginTop: 2,
  },
  sessionBadge: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  sessionText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  messagesList: {
    padding: 16,
    paddingBottom: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  messageContainer: {
    marginBottom: 16,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  botMessageContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 12,
  },
  userBubble: {
    backgroundColor: '#6A11CB',
  },
  botBubble: {
    backgroundColor: '#fff',
    borderColor: '#E0E0E0',
    borderWidth: 1,
  },
  messageText: {
    fontSize: 15,
  },
  userMessageText: {
    color: '#fff',
  },
  botMessageText: {
    color: '#333',
  },
  timestamp: {
    fontSize: 11,
    color: '#999',
    marginTop: 6,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderTopWidth: 1,
    borderColor: '#E0E0E0',
    backgroundColor: '#fff',
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 120,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#F2F2F2',
    borderRadius: 20,
    marginRight: 8,
    color: '#333',
  },
  sendButton: {
    backgroundColor: '#6A11CB',
    padding: 10,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#9E8FBF',
  },
  humanFormOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  humanFormContainer: {
    width: '90%',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
  },
  formHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  formTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  formSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  formInput: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
    color: '#333',
  },
  problemInput: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#6A11CB',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#fff',
    fontWeight: '600',
  }
  
});

export default ChatScreen;

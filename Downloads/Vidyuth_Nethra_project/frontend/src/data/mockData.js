// mockData.js – Simulated backend data

export const currentUser = {
  name: "Arjun",
  email: "arjun@example.com",
  avatar: "AR",
};

export const homes = [
  { id: 1, name: "Green Villa", location: "Bangalore, Karnataka", status: "active", image: "🏡" },
  { id: 2, name: "City Apartment", location: "Bangalore, Karnataka", status: "active", image: "🏢" },
  { id: 3, name: "Weekend Home", location: "Mysore, Karnataka", status: "active", image: "🏠" },
];

export const statsData = {
  totalConsumption: { value: "42.6", unit: "kWh", label: "Today", trend: "+2.3%" },
  predictedUsage: { value: "58.3", unit: "kWh", label: "Tomorrow", trend: "-1.1%" },
  estimatedBill: { value: "₹1,245", unit: "", label: "This Month", trend: "+₹88" },
  totalSavings: { value: "₹352", unit: "", label: "This Month", trend: "+₹52" },
};

export const hourlyUsage = [
  { time: "12 AM", today: 2.1, yesterday: 2.4 },
  { time: "2 AM", today: 1.8, yesterday: 1.9 },
  { time: "4 AM", today: 1.5, yesterday: 1.7 },
  { time: "6 AM", today: 3.2, yesterday: 2.8 },
  { time: "8 AM", today: 5.6, yesterday: 4.9 },
  { time: "10 AM", today: 7.2, yesterday: 6.5 },
  { time: "12 PM", today: 8.4, yesterday: 7.8 },
  { time: "2 PM", today: 9.1, yesterday: 8.3 },
  { time: "4 PM", today: 9.8, yesterday: 9.0 },
  { time: "6 PM", today: 8.7, yesterday: 8.2 },
  { time: "8 PM", today: 7.3, yesterday: 7.0 },
  { time: "10 PM", today: 4.2, yesterday: 5.1 },
  { time: "12 AM", today: 2.8, yesterday: 3.2 },
];

export const topDevices = [
  { name: "AC", room: "Living Room", usage: 12.6, percent: 29, icon: "❄️", color: "#3b82f6" },
  { name: "Water Heater", room: "Bathroom", usage: 8.7, percent: 20, icon: "🔥", color: "#f59e0b" },
  { name: "Refrigerator", room: "Kitchen", usage: 6.2, percent: 15, icon: "🧊", color: "#06b6d4" },
  { name: "Washing Machine", room: "Utility", usage: 4.1, percent: 10, icon: "🌀", color: "#8b5cf6" },
  { name: "Others", room: "", usage: 11.0, percent: 26, icon: "⚡", color: "#6b7280" },
];

export const aiRecommendations = [
  {
    id: 1,
    icon: "❄️",
    color: "#10b981",
    bgColor: "rgba(16,185,129,0.1)",
    message: "Your AC has been running for 6+ hours. Consider increasing temperature by 1-2°C to save energy.",
    saving: "₹120",
    priority: "high",
  },
  {
    id: 2,
    icon: "💡",
    color: "#f59e0b",
    bgColor: "rgba(245,158,11,0.1)",
    message: "4 lights are on in empty rooms. Turn them off to save energy.",
    saving: "₹45",
    priority: "medium",
  },
  {
    id: 3,
    icon: "🌀",
    color: "#3b82f6",
    bgColor: "rgba(59,130,246,0.1)",
    message: "Fan speed is high. Medium speed is sufficient and saves more energy.",
    saving: "₹30",
    priority: "low",
  },
];

export const recentActivity = [
  { id: 1, icon: "❄️", message: "AC (Living Room) turned ON", time: "Today, 10:30 AM", type: "device" },
  { id: 2, icon: "🧊", message: "Refrigerator is running normally", time: "Today, 09:15 AM", type: "status" },
  { id: 3, icon: "📊", message: "Monthly report generated", time: "Yesterday, 11:45 PM", type: "report" },
  { id: 4, icon: "💰", message: "You saved ₹52 yesterday", time: "Yesterday, 10:00 PM", type: "saving" },
];

export const devices = [
  { id: 1, name: "AC", room: "Living Room", status: "on", type: "ac", power: 1500, icon: "❄️" },
  { id: 2, name: "Fan", room: "Living Room", status: "on", type: "fan", power: 75, icon: "🌀" },
  { id: 3, name: "Light", room: "Living Room", status: "off", type: "light", power: 15, icon: "💡" },
  { id: 4, name: "AC", room: "Bedroom", status: "off", type: "ac", power: 1200, icon: "❄️" },
  { id: 5, name: "Light", room: "Bedroom", status: "on", type: "light", power: 10, icon: "💡" },
  { id: 6, name: "Water Heater", room: "Bathroom", status: "on", type: "heater", power: 2000, icon: "🔥" },
  { id: 7, name: "Refrigerator", room: "Kitchen", status: "on", type: "fridge", power: 150, icon: "🧊" },
  { id: 8, name: "Light", room: "Kitchen", status: "on", type: "light", power: 20, icon: "💡" },
];

export const chatHistory = [
  {
    id: 1,
    role: "bot",
    message: "Hello Arjun! 👋 I'm your energy assistant. How can I help you today?",
    time: "10:30 AM",
  },
];

export const weeklyUsage = [
  { day: "Mon", usage: 38.2 },
  { day: "Tue", usage: 41.5 },
  { day: "Wed", usage: 44.8 },
  { day: "Thu", usage: 39.1 },
  { day: "Fri", usage: 46.3 },
  { day: "Sat", usage: 52.7 },
  { day: "Sun", usage: 42.6 },
];

export const translations = {
  en: {
    dashboard: "Dashboard",
    myHomes: "My Homes",
    devices: "Devices",
    energyUsage: "Energy Usage",
    aiRecommendations: "AI Recommendations",
    voiceAssistant: "Voice Assistant",
    chatAssistant: "Chat Assistant",
    reports: "Reports",
    settings: "Settings",
    logout: "Logout",
    totalConsumption: "Total Consumption",
    predictedUsage: "Predicted Usage",
    estimatedBill: "Estimated Bill",
    totalSavings: "Total Savings",
    currentUsageOverview: "Current Usage Overview",
    topConsumingDevices: "Top Consuming Devices",
    recentActivity: "Recent Activity",
    viewAll: "View All",
    potentialSaving: "Potential Saving",
    today: "Today",
    yesterday: "Yesterday",
    welcomeBack: "Welcome back",
    subtitle: "Here's what's happening in your smart homes today.",
    turnOff: "Turn Off",
    turnOn: "Turn On",
    addDevice: "Add Device",
    language: "Language",
  },
  hi: {
    dashboard: "डैशबोर्ड",
    myHomes: "मेरे घर",
    devices: "उपकरण",
    energyUsage: "ऊर्जा उपयोग",
    aiRecommendations: "AI सुझाव",
    voiceAssistant: "वॉइस असिस्टेंट",
    chatAssistant: "चैट असिस्टेंट",
    reports: "रिपोर्ट",
    settings: "सेटिंग्स",
    logout: "लॉग आउट",
    totalConsumption: "कुल खपत",
    predictedUsage: "अनुमानित उपयोग",
    estimatedBill: "अनुमानित बिल",
    totalSavings: "कुल बचत",
    currentUsageOverview: "वर्तमान उपयोग अवलोकन",
    topConsumingDevices: "सर्वाधिक खपत उपकरण",
    recentActivity: "हालिया गतिविधि",
    viewAll: "सभी देखें",
    potentialSaving: "संभावित बचत",
    today: "आज",
    yesterday: "कल",
    welcomeBack: "वापसी पर स्वागत है",
    subtitle: "आज आपके स्मार्ट घरों में क्या हो रहा है।",
    turnOff: "बंद करें",
    turnOn: "चालू करें",
    addDevice: "उपकरण जोड़ें",
    language: "भाषा",
  },
  te: {
    dashboard: "డాష్‌బోర్డ్",
    myHomes: "నా ఇళ్ళు",
    devices: "పరికరాలు",
    energyUsage: "శక్తి వినియోగం",
    aiRecommendations: "AI సూచనలు",
    voiceAssistant: "వాయిస్ అసిస్టెంట్",
    chatAssistant: "చాట్ అసిస్టెంట్",
    reports: "నివేదికలు",
    settings: "సెట్టింగ్‌లు",
    logout: "లాగ్ అవుట్",
    totalConsumption: "మొత్తం వినియోగం",
    predictedUsage: "అంచనా వినియోగం",
    estimatedBill: "అంచనా బిల్లు",
    totalSavings: "మొత్తం పొదుపు",
    currentUsageOverview: "ప్రస్తుత వినియోగ అవలోకనం",
    topConsumingDevices: "అధిక వినియోగ పరికరాలు",
    recentActivity: "ఇటీవలి కార్యకలాపం",
    viewAll: "అన్నీ చూడండి",
    potentialSaving: "సంభావ్య పొదుపు",
    today: "ఈరోజు",
    yesterday: "నిన్న",
    welcomeBack: "తిరిగి స్వాగతం",
    subtitle: "ఈరోజు మీ స్మార్ట్ హోమ్‌లలో ఏమి జరుగుతుందో ఇక్కడ ఉంది.",
    turnOff: "ఆపివేయి",
    turnOn: "చాలు",
    addDevice: "పరికరం జోడించు",
    language: "భాష",
  },
};

export const monthlyData = [
  { month: 'Jan', usage: 1120, bill: 3360 },
  { month: 'Feb', usage: 980, bill: 2940 },
  { month: 'Mar', usage: 1050, bill: 3150 },
  { month: 'Apr', usage: 1340, bill: 4020 },
  { month: 'May', usage: 1480, bill: 4440 },
  { month: 'Jun', usage: 1245, bill: 3735 },
];

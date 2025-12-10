import ChatBot from '@/components/ChatBot';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4 md:p-6 lg:p-8">
      <div className="w-full max-w-4xl h-[85vh] md:h-[80vh] lg:h-[75vh]">
        <ChatBot />
      </div>
    </main>
  );
}

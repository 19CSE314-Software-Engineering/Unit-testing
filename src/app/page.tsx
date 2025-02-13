// Next.js Supabase Auth Component with Proper Password Reset Handling
'use client';
import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { useRouter } from 'next/navigation';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL ?? '',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''
);

export default function Auth() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const router = useRouter();

  const signIn = async () => {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) alert(error.message);
  };

  const signUp = async () => {
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) alert(error.message);
  };

  const resetPassword = async () => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback`
    });
    alert(error ? error.message : 'Password reset link sent to your email.');
  };

  useEffect(() => {
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) router.push('/dashboard');
    });
    return () => listener?.subscription.unsubscribe();
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4 text-black">
      <div className="bg-white shadow-lg rounded-2xl p-6 w-96">
        {showForgotPassword ? (
          <>
            <h2 className="text-2xl font-bold mb-4">Forgot Password</h2>
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full mb-3 p-2 border rounded-lg" />
            <button onClick={resetPassword} className="w-full bg-yellow-500 text-white py-2 px-4 rounded-lg hover:bg-yellow-600">Send Reset Link</button>
            <button onClick={() => setShowForgotPassword(false)} className="w-full mt-3 text-blue-500 hover:underline">Back to Login</button>
          </>
        ) : (
          <>
            <h2 className="text-2xl font-bold mb-4">Login / Signup</h2>
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full mb-3 p-2 border rounded-lg" />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full mb-4 p-2 border rounded-lg" />
            <div className="flex justify-between mb-2">
              <button onClick={signIn} className="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">Sign In</button>
              <button onClick={signUp} className="bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600">Sign Up</button>
            </div>
            <button onClick={() => setShowForgotPassword(true)} className="text-blue-500 hover:underline">Forgot Password?</button>
          </>
        )}
      </div>
    </div>
  );
}

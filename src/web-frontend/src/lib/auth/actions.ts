'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

/**
 * Sign out the current user
 */
export async function signOut(locale: string = 'en') {
  const supabase = await createClient()

  const { error } = await supabase.auth.signOut()

  if (error) {
    console.error('Error signing out:', error)
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  redirect(`/${locale}/login`)
}

/**
 * Get the current user
 */
export async function getUser() {
  const supabase = await createClient()

  const {
    data: { user },
    error
  } = await supabase.auth.getUser()

  if (error) {
    console.error('Error getting user:', error)
    return null
  }

  return user
}

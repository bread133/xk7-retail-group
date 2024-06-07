import { ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from '@/consts'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function validateFileSize(file: File): boolean {
  return file.size <= MAX_FILE_SIZE
}

export function validateFileType(file: File): boolean {
  return ALLOWED_FILE_TYPES.includes(file.type)
}

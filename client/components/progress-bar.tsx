import { cn } from '@/lib/utils'

interface ProgressBarProps {
  progress: number
  isError?: boolean
  className?: string
}

export const ProgressBar = ({ className, progress }: ProgressBarProps) => {
  return (
    <div
      className={cn(
        'max-w-[130px] bg-gray-200 rounded-full h-2.5 bg-gray-700',
        className
      )}
    >
      <div
        className='bg-slate-400 h-2 rounded-full'
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  )
}

interface BorrowingItemProps {
  nameVideo: string
  id: string
  originalLink: string
  start: string
  end: string
}

export const BorrowingItem = ({
  end,
  id,
  nameVideo,
  originalLink,
  start
}: BorrowingItemProps) => {
  return (
    <tr>
      <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500'>
        {nameVideo}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500'>
        {id}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500'>
        {originalLink}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500'>
        {start}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500'>
        {end}
      </td>
    </tr>
  )
}

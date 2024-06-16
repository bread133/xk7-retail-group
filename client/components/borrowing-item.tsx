interface BorrowingItemProps {
  title_license: string
  title_piracy: string
  time_license_start: number
  time_license_finish: number
  time_piracy_start: number
  time_piracy_finish: number
}

export const BorrowingItem = ({
  time_license_finish,
  time_license_start,
  time_piracy_finish,
  time_piracy_start,
  title_license,
  title_piracy
}: BorrowingItemProps) => {
  return (
    <tr>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {title_license}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {title_piracy}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {time_piracy_start}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {time_piracy_finish}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {time_license_start}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-slate-500'>
        {time_license_finish}
      </td>
    </tr>
  )
}

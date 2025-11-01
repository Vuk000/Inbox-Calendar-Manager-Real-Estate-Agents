"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { contactsService } from "@/lib/api"
import toast from "react-hot-toast"
import { Loader2 } from "lucide-react"

const contactSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().optional(),
  company: z.string().optional(),
  job_title: z.string().optional(),
  address_line1: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip_code: z.string().optional(),
  contact_type: z.string().optional(),
  contact_status: z.string().optional(),
  relationship_score: z.number().min(0).max(1).optional(),
  notes: z.string().optional(),
})

type ContactFormData = z.infer<typeof contactSchema>

interface ContactCreateDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
  initialData?: Partial<ContactFormData> & { id?: number }
}

export function ContactCreateDialog({ open, onOpenChange, onSuccess, initialData }: ContactCreateDialogProps) {
  const [isLoading, setIsLoading] = useState(false)
  const isEditMode = !!initialData && 'id' in initialData

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      contact_type: "buyer",
      contact_status: "cold_lead",
    },
  })

  // Reset form when initialData changes (for edit mode)
  useEffect(() => {
    if (initialData) {
      reset({
        ...initialData,
        contact_type: initialData.contact_type || "buyer",
        contact_status: initialData.contact_status || "cold_lead",
      })
    } else {
      reset({
        contact_type: "buyer",
        contact_status: "cold_lead",
      })
    }
  }, [initialData, reset])

  const contactType = watch("contact_type")
  const contactStatus = watch("contact_status")

  const onSubmit = async (data: ContactFormData) => {
    setIsLoading(true)
    try {
      if (isEditMode && initialData && 'id' in initialData && initialData.id !== undefined) {
        await contactsService.updateContact(initialData.id, data)
        toast.success("Contact updated successfully!")
      } else {
        await contactsService.createContact(data)
        toast.success("Contact created successfully!")
      }
      reset()
      onSuccess?.()
      onOpenChange(false)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'create'} contact`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    reset()
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={(newOpen) => {
      if (!newOpen) {
        handleClose()
      } else {
        onOpenChange(newOpen)
      }
    }}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditMode ? "Edit Contact" : "Create New Contact"}</DialogTitle>
          <DialogDescription>
            {isEditMode ? "Update contact information" : "Add a new contact to your database"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">First Name *</Label>
              <Input
                id="first_name"
                {...register("first_name")}
                className={errors.first_name ? "border-destructive" : ""}
              />
              {errors.first_name && (
                <p className="text-sm text-destructive">{errors.first_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Last Name *</Label>
              <Input
                id="last_name"
                {...register("last_name")}
                className={errors.last_name ? "border-destructive" : ""}
              />
              {errors.last_name && <p className="text-sm text-destructive">{errors.last_name.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                {...register("email")}
                className={errors.email ? "border-destructive" : ""}
              />
              {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input id="phone" {...register("phone")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company">Company</Label>
              <Input id="company" {...register("company")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="job_title">Job Title</Label>
              <Input id="job_title" {...register("job_title")} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="address_line1">Address</Label>
            <Input id="address_line1" {...register("address_line1")} />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input id="city" {...register("city")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="state">State</Label>
              <Input id="state" {...register("state")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="zip_code">Zip Code</Label>
              <Input id="zip_code" {...register("zip_code")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact_type">Contact Type</Label>
              <Select
                value={contactType || "buyer"}
                onValueChange={(value) => setValue("contact_type", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="buyer">Buyer</SelectItem>
                  <SelectItem value="seller">Seller</SelectItem>
                  <SelectItem value="investor">Investor</SelectItem>
                  <SelectItem value="lender">Lender</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact_status">Status</Label>
              <Select
                value={contactStatus || "cold_lead"}
                onValueChange={(value) => setValue("contact_status", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cold_lead">Cold Lead</SelectItem>
                  <SelectItem value="warm_lead">Warm Lead</SelectItem>
                  <SelectItem value="hot_lead">Hot Lead</SelectItem>
                  <SelectItem value="active">Active Client</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="contract_pending">Contract Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea id="notes" {...register("notes")} rows={4} />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {isEditMode ? "Updating..." : "Creating..."}
                </>
              ) : (
                isEditMode ? "Update Contact" : "Create Contact"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}


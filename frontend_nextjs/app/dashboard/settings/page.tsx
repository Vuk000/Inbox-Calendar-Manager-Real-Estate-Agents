"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { User, Bell, Lock, CreditCard, Palette, Globe, Zap, Loader2, AlertCircle, Check, X } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { authService, integrationService } from "@/lib/api"
import { useAuthStore } from "@/lib/stores/authStore"
import toast from "react-hot-toast"

const passwordChangeSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string().min(1, "Please confirm your password"),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
})

type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState("profile")

  // Fetch current user data
  const { data: userData, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      try {
        return await authService.getCurrentUser()
      } catch (error) {
        return user || null
      }
    },
  })

  // Fetch email accounts
  const { data: emailAccounts = [] } = useQuery({
    queryKey: ['emailAccounts'],
    queryFn: async () => {
      try {
        return await integrationService.listEmailAccounts()
      } catch (error) {
        return []
      }
    },
  })

  const currentUser = userData || user

  // Profile update mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (data: { full_name?: string; phone_number?: string }) => {
      return await authService.updateProfile(data)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user'] })
      useAuthStore.getState().updateUser(data)
      toast.success('Profile updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update profile')
    },
  })

  // Password change mutation
  const changePasswordMutation = useMutation({
    mutationFn: async (data: { current_password: string; new_password: string }) => {
      return await authService.changePassword(data)
    },
    onSuccess: () => {
      toast.success('Password changed successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to change password')
    },
  })

  const handleProfileUpdate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    updateProfileMutation.mutate({
      full_name: formData.get('full_name') as string || undefined,
      phone_number: formData.get('phone_number') as string || undefined,
    })
  }

  const passwordForm = useForm<PasswordChangeFormData>({
    resolver: zodResolver(passwordChangeSchema),
  })

  const handlePasswordChange = passwordForm.handleSubmit((data) => {
    changePasswordMutation.mutate({
      current_password: data.current_password,
      new_password: data.new_password,
    }, {
      onSuccess: () => {
        passwordForm.reset()
      }
    })
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-balance">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account and preferences</p>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card cursor-pointer hover:glow-border transition-all">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold">Billing</p>
                <p className="text-xs text-muted-foreground">Manage subscription</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card cursor-pointer hover:glow-border transition-all">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500 flex items-center justify-center">
                <Palette className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold">Appearance</p>
                <p className="text-xs text-muted-foreground">Theme settings</p>
              </div>
            </CardContent>
        </Card>
        <Card className="glass-card cursor-pointer hover:glow-border transition-all">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center">
                <Globe className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold">Integrations</p>
                <p className="text-xs text-muted-foreground">{emailAccounts.length} connected</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card cursor-pointer hover:glow-border transition-all">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold">API Keys</p>
                <p className="text-xs text-muted-foreground">Developer access</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Profile Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : (
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input 
                      id="full_name" 
                      name="full_name"
                      defaultValue={currentUser?.full_name || ""} 
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" defaultValue={currentUser?.email || ""} disabled />
                    <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone_number">Phone Number</Label>
                    <Input 
                      id="phone_number" 
                      name="phone_number"
                      type="tel" 
                      defaultValue={currentUser?.phone_number || ""} 
                    />
                  </div>
                  <div className="pt-4 border-t border-border">
                    <Badge variant="outline" className="capitalize">
                      {currentUser?.role || "User"}
                    </Badge>
                    <Badge variant="secondary" className="ml-2 capitalize">
                      {currentUser?.subscription_tier?.replace(/_/g, " ") || "Free"} Plan
                    </Badge>
                  </div>
                  <Button type="submit" disabled={updateProfileMutation.isPending} className="glow-border">
                    {updateProfileMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      "Save Changes"
                    )}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations Tab */}
        <TabsContent value="integrations">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Email Integrations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {emailAccounts.length === 0 ? (
                <div className="text-center py-8">
                  <Globe className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground mb-4">No email accounts connected</p>
                  <Button>
                    <Globe className="w-4 h-4 mr-2" />
                    Connect Gmail
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {emailAccounts.map((account: any) => (
                    <div key={account.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Globe className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-semibold">{account.email_address}</p>
                          <p className="text-xs text-muted-foreground capitalize">
                            {account.provider} • {account.sync_status}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {account.is_active ? (
                          <Badge variant="default" className="bg-green-500">
                            <Check className="w-3 h-3 mr-1" />
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <X className="w-3 h-3 mr-1" />
                            Inactive
                          </Badge>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={async () => {
                            try {
                              await integrationService.disconnectEmailAccount(account.id)
                              queryClient.invalidateQueries({ queryKey: ['emailAccounts'] })
                              toast.success('Email account disconnected')
                            } catch (error: any) {
                              toast.error(error.response?.data?.detail || 'Failed to disconnect')
                            }
                          }}
                        >
                          Disconnect
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button className="w-full">
                    <Globe className="w-4 h-4 mr-2" />
                    Connect New Email Account
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notification Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-border">
                <div>
                  <Label htmlFor="email-notifications">Email Notifications</Label>
                  <p className="text-xs text-muted-foreground">Receive email alerts</p>
                </div>
                <Switch id="email-notifications" defaultChecked />
              </div>
              <div className="flex items-center justify-between py-3 border-b border-border">
                <div>
                  <Label htmlFor="desktop-notifications">Desktop Notifications</Label>
                  <p className="text-xs text-muted-foreground">Browser notifications</p>
                </div>
                <Switch id="desktop-notifications" />
              </div>
              <div className="flex items-center justify-between py-3 border-b border-border">
                <div>
                  <Label htmlFor="weekly-reports">Weekly Reports</Label>
                  <p className="text-xs text-muted-foreground">Summary emails</p>
                </div>
                <Switch id="weekly-reports" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Security Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current_password">Current Password</Label>
                  <Input 
                    id="current_password" 
                    type="password" 
                    {...passwordForm.register("current_password")}
                    className={passwordForm.formState.errors.current_password ? "border-destructive" : ""}
                  />
                  {passwordForm.formState.errors.current_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.current_password.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password</Label>
                  <Input 
                    id="new_password" 
                    type="password" 
                    {...passwordForm.register("new_password")}
                    className={passwordForm.formState.errors.new_password ? "border-destructive" : ""}
                  />
                  {passwordForm.formState.errors.new_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.new_password.message}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">Must be at least 8 characters</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm New Password</Label>
                  <Input 
                    id="confirm_password" 
                    type="password" 
                    {...passwordForm.register("confirm_password")}
                    className={passwordForm.formState.errors.confirm_password ? "border-destructive" : ""}
                  />
                  {passwordForm.formState.errors.confirm_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.confirm_password.message}
                    </p>
                  )}
                </div>
                <Button 
                  type="submit" 
                  disabled={changePasswordMutation.isPending || passwordForm.formState.isSubmitting}
                  className="glow-border"
                >
                  {changePasswordMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Changing...
                    </>
                  ) : (
                    "Change Password"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

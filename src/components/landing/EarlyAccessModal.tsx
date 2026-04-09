import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { supabase } from "@/integrations/supabase/client";
import { ArrowRight, CheckCircle2, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface EarlyAccessModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const EarlyAccessModal = ({ open, onOpenChange }: EarlyAccessModalProps) => {
  const { toast } = useToast();
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    clinic_name: "",
    role: "",
    phone: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.full_name.trim()) errs.full_name = "Full name is required";
    if (!form.email.trim()) errs.email = "Email is required";
    else if (!EMAIL_REGEX.test(form.email.trim())) errs.email = "Enter a valid email";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke("submit-early-access", {
        body: {
          full_name: form.full_name.trim(),
          email: form.email.trim(),
          clinic_name: form.clinic_name.trim() || undefined,
          role: form.role.trim() || undefined,
          phone: form.phone.trim() || undefined,
        },
      });

      if (error) throw error;
      if (data?.error) throw new Error(data.error);

      setSubmitted(true);
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Submission failed",
        description: err?.message || "Something went wrong. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = (isOpen: boolean) => {
    if (!isOpen) {
      // Reset form after close animation
      setTimeout(() => {
        setSubmitted(false);
        setForm({ full_name: "", email: "", clinic_name: "", role: "", phone: "" });
        setErrors({});
      }, 300);
    }
    onOpenChange(isOpen);
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: "" }));
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[480px] bg-card border-border">
        {submitted ? (
          <div className="py-8 text-center">
            <CheckCircle2 className="w-14 h-14 text-accent mx-auto mb-4" />
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-foreground">
                You're on the list!
              </DialogTitle>
              <DialogDescription className="text-muted-foreground mt-2 text-[15px] leading-relaxed">
                Thanks for your interest in Benchmark PS. We've sent a confirmation to your email
                and someone from the team will be in touch within 1–2 working days.
              </DialogDescription>
            </DialogHeader>
            <Button
              onClick={() => handleClose(false)}
              className="mt-6 bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              Close
            </Button>
          </div>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="text-xl font-bold text-foreground">
                Request Early Access
              </DialogTitle>
              <DialogDescription className="text-muted-foreground text-[14px]">
                Fill in your details and we'll reach out to set up your clinic.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4 mt-2">
              <div className="space-y-1.5">
                <Label htmlFor="ea-name" className="text-foreground text-[13px] font-medium">
                  Full Name <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="ea-name"
                  value={form.full_name}
                  onChange={(e) => updateField("full_name", e.target.value)}
                  placeholder="Dr. Jane Smith"
                  maxLength={200}
                  className="bg-background border-input"
                />
                {errors.full_name && (
                  <p className="text-destructive text-xs">{errors.full_name}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="ea-email" className="text-foreground text-[13px] font-medium">
                  Email <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="ea-email"
                  type="email"
                  value={form.email}
                  onChange={(e) => updateField("email", e.target.value)}
                  placeholder="jane@clinic.com"
                  maxLength={255}
                  className="bg-background border-input"
                />
                {errors.email && (
                  <p className="text-destructive text-xs">{errors.email}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="ea-clinic" className="text-foreground text-[13px] font-medium">
                  Clinic / Organisation
                </Label>
                <Input
                  id="ea-clinic"
                  value={form.clinic_name}
                  onChange={(e) => updateField("clinic_name", e.target.value)}
                  placeholder="City Physiotherapy"
                  maxLength={200}
                  className="bg-background border-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="ea-role" className="text-foreground text-[13px] font-medium">
                    Role
                  </Label>
                  <Input
                    id="ea-role"
                    value={form.role}
                    onChange={(e) => updateField("role", e.target.value)}
                    placeholder="Physiotherapist"
                    maxLength={100}
                    className="bg-background border-input"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="ea-phone" className="text-foreground text-[13px] font-medium">
                    Phone
                  </Label>
                  <Input
                    id="ea-phone"
                    type="tel"
                    value={form.phone}
                    onChange={(e) => updateField("phone", e.target.value)}
                    placeholder="+44 7700 000000"
                    maxLength={30}
                    className="bg-background border-input"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-5 text-[15px] font-semibold rounded-lg mt-2"
              >
                {loading ? (
                  <><Loader2 className="mr-2 w-4 h-4 animate-spin" /> Submitting…</>
                ) : (
                  <>Submit Request <ArrowRight className="ml-2 w-4 h-4" /></>
                )}
              </Button>

              <p className="text-muted-foreground text-[11px] text-center leading-relaxed">
                By submitting, you agree to be contacted by Benchmark PS about the platform.
              </p>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default EarlyAccessModal;
